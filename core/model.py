from PIL import Image
from transformers import AutoTokenizer, AutoProcessor
import torch
from transformers import AutoConfig, AutoModel
print(torch.cuda.is_available())
print(torch.version.cuda)
class Model():
    def __init__(self):
        self.model_path = 'mPLUG/mPLUG-Owl3-2B-241014'
        self.config = AutoConfig.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(self.model_path, attn_implementation='sdpa', torch_dtype=torch.half, trust_remote_code=True)
        self.model.eval().cuda()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.processor = self.model.init_processor(self.tokenizer)

    def generate(self, messages, images=None, videos=None):
        inputs = self.processor(messages,images=None, videos=None)
        inputs.to('cuda')
        inputs.update({
            'tokenizer': self.tokenizer,
            'max_new_tokens':100,
            'decode_text':True,
        })
        g = self.model.generate(**inputs)
        return g
