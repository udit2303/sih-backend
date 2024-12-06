from PIL import Image
from transformers import AutoTokenizer, AutoProcessor
import torch
from transformers import AutoConfig, AutoModel
print(torch.cuda.is_available())
print(torch.version.cuda)

model_path = 'mPLUG/mPLUG-Owl3-2B-241014'
config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
print(config)
# model = mPLUGOwl3Model(config).cuda().half()
model = AutoModel.from_pretrained(model_path, attn_implementation='sdpa', torch_dtype=torch.half, trust_remote_code=True)
model.eval().cuda()

model_path = 'mPLUG/mPLUG-Owl3-2B-241014'
tokenizer = AutoTokenizer.from_pretrained(model_path)
processor = model.init_processor(tokenizer)

image = Image.new('RGB', (500, 500), color='red')

messages = [
    {"role": "user", "content": """<|image|>
Describe this image."""},
    {"role": "assistant", "content": ""}
]

inputs = processor(messages, images=[image], videos=None)

inputs.to('cuda')
inputs.update({
    'tokenizer': tokenizer,
    'max_new_tokens':100,
    'decode_text':True,
})


g = model.generate(**inputs)
print(g)
