#!/usr/bin/env python3
import csv
import json
import logging
import os
import platform
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence, Tuple, Union

import numpy as np
import sklearn
import torch
import transformers

try:
    from peft import LoraConfig, get_peft_model
except Exception:
    # Allow non-LoRA runs even if peft/accelerate versions are mismatched.
    LoraConfig = None
    get_peft_model = None
from torch.utils.data import Dataset


@dataclass
class ModelArguments:
    model_name_or_path: str = field(default="zhihan1996/DNABERT-2-117M")
    use_lora: bool = field(default=False)
    lora_r: int = field(default=8)
    lora_alpha: int = field(default=16)
    lora_dropout: float = field(default=0.05)
    lora_target_modules: str = field(default="query,value")


@dataclass
class DataArguments:
    data_path: str = field(default=None)


@dataclass
class TrainingArguments(transformers.TrainingArguments):
    cache_dir: Optional[str] = field(default=None)
    run_name: str = field(default="run")
    model_max_length: int = field(default=128)
    optim: str = field(default="adamw_torch")
    eval_and_save_results: bool = field(default=True)
    save_model: bool = field(default=False)
    dataloader_pin_memory: bool = field(default=False)
    report_to: str = field(default="none")


class SupervisedDataset(Dataset):
    def __init__(self, data_file: str, tokenizer: transformers.PreTrainedTokenizer):
        with open(data_file, "r") as f:
            rows = list(csv.reader(f))
        header = [h.strip().lower() for h in rows[0]]
        if "sequence" not in header or "label" not in header:
            raise ValueError(f"{data_file} must include header: sequence,label")

        seq_idx = header.index("sequence")
        label_idx = header.index("label")

        texts = [row[seq_idx].strip() for row in rows[1:] if row]
        labels = [int(row[label_idx]) for row in rows[1:] if row]

        encoded = tokenizer(
            texts,
            return_tensors="pt",
            padding="longest",
            max_length=tokenizer.model_max_length,
            truncation=True,
        )
        self.input_ids = encoded["input_ids"]
        self.attention_mask = encoded["attention_mask"]
        self.labels = labels
        self.num_labels = len(set(labels))

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }


@dataclass
class DataCollatorForSupervisedDataset:
    tokenizer: transformers.PreTrainedTokenizer

    def __call__(self, instances: Sequence[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        input_ids = [instance["input_ids"] for instance in instances]
        labels = [instance["labels"] for instance in instances]
        input_ids = torch.nn.utils.rnn.pad_sequence(
            input_ids, batch_first=True, padding_value=self.tokenizer.pad_token_id
        )
        labels = torch.stack(labels)
        return {
            "input_ids": input_ids,
            "labels": labels,
            "attention_mask": input_ids.ne(self.tokenizer.pad_token_id),
        }


def safe_metric(fn, default=np.nan):
    try:
        return fn()
    except Exception:
        return default


def compute_metrics(eval_pred: Tuple[np.ndarray, np.ndarray]) -> Dict[str, float]:
    logits, labels = eval_pred
    if isinstance(logits, tuple):
        logits = logits[0]
    preds = np.argmax(logits, axis=-1)

    metrics = {
        "accuracy": sklearn.metrics.accuracy_score(labels, preds),
        "f1_macro": sklearn.metrics.f1_score(labels, preds, average="macro", zero_division=0),
        "matthews_correlation": sklearn.metrics.matthews_corrcoef(labels, preds),
        "precision_macro": sklearn.metrics.precision_score(labels, preds, average="macro", zero_division=0),
        "recall_macro": sklearn.metrics.recall_score(labels, preds, average="macro", zero_division=0),
    }

    probs = torch.softmax(torch.tensor(logits), dim=-1).cpu().numpy()
    num_labels = probs.shape[1]

    if num_labels == 2:
        pos_prob = probs[:, 1]
        metrics["auroc"] = safe_metric(lambda: sklearn.metrics.roc_auc_score(labels, pos_prob))
        metrics["auprc"] = safe_metric(lambda: sklearn.metrics.average_precision_score(labels, pos_prob))
    else:
        y_bin = sklearn.preprocessing.label_binarize(labels, classes=list(range(num_labels)))
        metrics["auroc"] = safe_metric(
            lambda: sklearn.metrics.roc_auc_score(y_bin, probs, average="macro", multi_class="ovr")
        )
        metrics["auprc"] = safe_metric(lambda: sklearn.metrics.average_precision_score(y_bin, probs, average="macro"))

    return metrics


def train() -> None:
    parser = transformers.HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    wall_start = time.time()

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
        model_max_length=training_args.model_max_length,
        padding_side="right",
        use_fast=True,
        trust_remote_code=True,
    )

    train_dataset = SupervisedDataset(os.path.join(data_args.data_path, "train.csv"), tokenizer)
    dev_dataset = SupervisedDataset(os.path.join(data_args.data_path, "dev.csv"), tokenizer)
    test_dataset = SupervisedDataset(os.path.join(data_args.data_path, "test.csv"), tokenizer)
    data_collator = DataCollatorForSupervisedDataset(tokenizer=tokenizer)

    # Use base BertConfig to avoid config-class mismatch with remote-code dynamic modules.
    from transformers.models.bert.configuration_bert import BertConfig

    config = BertConfig.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
    )
    # Some remote DNABERT-2 config revisions may miss pad token metadata in newer HF versions.
    if getattr(config, "pad_token_id", None) is None:
        config.pad_token_id = tokenizer.pad_token_id
    if getattr(config, "eos_token_id", None) is None and tokenizer.eos_token_id is not None:
        config.eos_token_id = tokenizer.eos_token_id
    if getattr(config, "bos_token_id", None) is None and tokenizer.bos_token_id is not None:
        config.bos_token_id = tokenizer.bos_token_id
    # DNABERT-2 remote code uses Triton flash-attn when attention dropout is 0.
    # On some Colab GPUs (e.g., T4), Triton kernel can exceed shared-memory limits.
    # Force non-zero attention dropout to use the safe PyTorch attention path.
    if getattr(config, "attention_probs_dropout_prob", 0.0) == 0.0:
        config.attention_probs_dropout_prob = 0.1
    config.num_labels = train_dataset.num_labels

    model = transformers.AutoModelForSequenceClassification.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
        trust_remote_code=True,
        config=config,
    )

    if model_args.use_lora:
        if LoraConfig is None or get_peft_model is None:
            raise ImportError(
                "LoRA is requested but peft is not available. "
                "Install compatible versions of peft/accelerate."
            )
        lora_cfg = LoraConfig(
            r=model_args.lora_r,
            lora_alpha=model_args.lora_alpha,
            target_modules=list(model_args.lora_target_modules.split(",")),
            lora_dropout=model_args.lora_dropout,
            bias="none",
            task_type="SEQ_CLS",
            inference_mode=False,
        )
        model = get_peft_model(model, lora_cfg)
        model.print_trainable_parameters()

    trainer = transformers.Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        compute_metrics=compute_metrics,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        data_collator=data_collator,
    )

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    train_output = trainer.train()
    train_wall_time = time.time() - wall_start
    train_metrics = dict(train_output.metrics)
    train_metrics.update(
        {
            "wall_clock_seconds": train_wall_time,
            "train_examples": len(train_dataset),
            "dev_examples": len(dev_dataset),
            "test_examples": len(test_dataset),
            "data_path": data_args.data_path,
            "model_name_or_path": model_args.model_name_or_path,
            "model_max_length": training_args.model_max_length,
            "num_train_epochs": training_args.num_train_epochs,
            "max_steps": training_args.max_steps,
            "per_device_train_batch_size": training_args.per_device_train_batch_size,
            "gradient_accumulation_steps": training_args.gradient_accumulation_steps,
            "fp16": training_args.fp16,
            "use_lora": model_args.use_lora,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cuda_available": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "peak_gpu_memory_mb": (
                round(torch.cuda.max_memory_allocated(0) / (1024**2), 3) if torch.cuda.is_available() else None
            ),
            "peak_gpu_reserved_mb": (
                round(torch.cuda.max_memory_reserved(0) / (1024**2), 3) if torch.cuda.is_available() else None
            ),
        }
    )

    if training_args.save_model:
        trainer.save_model(training_args.output_dir)

    if training_args.eval_and_save_results:
        out_dir = os.path.join(training_args.output_dir, "results", training_args.run_name)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "train_results.json"), "w") as f:
            json.dump(train_metrics, f, indent=2)
        test_results = trainer.evaluate(eval_dataset=test_dataset)
        test_results.update(
            {
                "train_wall_clock_seconds": train_metrics["wall_clock_seconds"],
                "train_examples": len(train_dataset),
                "dev_examples": len(dev_dataset),
                "test_examples": len(test_dataset),
                "peak_gpu_memory_mb": train_metrics["peak_gpu_memory_mb"],
                "peak_gpu_reserved_mb": train_metrics["peak_gpu_reserved_mb"],
            }
        )
        with open(os.path.join(out_dir, "eval_results.json"), "w") as f:
            json.dump(test_results, f, indent=2)
        logging.warning("Saved eval results to %s", out_dir)


if __name__ == "__main__":
    train()
