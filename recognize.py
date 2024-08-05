# Copyright (c) 2024 Binbin Zhang(binbzha@qq.com)
from dataclasses import dataclass, field

from tqdm import tqdm
import torch
from torch.utils.data import DataLoader
import transformers
from transformers import AutoTokenizer

from train import (
    init_model,
    ModelArguments,
    DataArguments,
    SpeechDataset,
)


@dataclass
class DecodeArguments:
    max_new_tokens: int = 50
    num_beams: int = 1
    batch_size: int = 8
    result_path: str = field(default=None, metadata={"help": "Path to result"})


def main():
    parser = transformers.HfArgumentParser(
        (ModelArguments, DataArguments, DecodeArguments))
    model_args, data_args, decode_args = parser.parse_args_into_dataclasses()
    model = init_model(model_args)
    if torch.cuda.is_available():
        model = model.cuda()
    tokenizer = AutoTokenizer.from_pretrained(model_args.llm_model_name_or_path)
    test_dataset = SpeechDataset(data_args.data_path,
                                 tokenizer=tokenizer,
                                 inference=True)
    data_loader = DataLoader(test_dataset, batch_size=decode_args.batch_size)
    fid = open(decode_args.result_path, 'w', encoding='utf8')
    for item in tqdm(data_loader):
        generated_ids = model.generate(**item, decode_config=decode_args)
        text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        for t in text:
            fid.write(t + '\n')
    fid.close()


if __name__ == "__main__":
    main()