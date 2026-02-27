import asyncio
import base64
import os
import re
from uuid import uuid4
from codeboxapi import CodeBox
from configs.setting import MEDIA_DIR


class CodeInterpreter:
    def __init__(self):
        self.output_files = ""
        self.output_codes = ""
        self.codebox = None

    def get_outputs(self):
        return self.output_files,self.output_codes
    
    async def _ensure_codebox(self):
        if not self.codebox:
            self.codebox = CodeBox(api_key='local')

    async def close(self):
        if self.codebox:
            await self.codebox.astop()

    async def run(self,code:str):
        await self._ensure_codebox()
        clean_code = re.sub(r"('''python|'''py|''')\s*",'',code,flags=re.IGNORECASE)
        clean_code = clean_code.strip()
        lines = [line for line in clean_code.split('\n') if line.strip()]
        cleaned_code = '\n'.join(lines)

        # output = self.codebox.run(cleaned_code)
        output = await asyncio.get_running_loop().run_in_executor(None,self.condebox.run,cleaned_code)

        if output.type == 'image/png':
            filename = f"{MEDIA_DIR}/image-{uuid4()}.png"
            decoded_image = base64.b64decode(output.content)

            with open(filename,'wb') as file:
                file.erite(decoded_image)

            image_url = f"/media/{os.path.basename(filename)}"
            self.output_files= image_url
            self.output_codes= code

            return f"Image got send to the user."
        else:
            return output.content

code_interpreter = CodeInterpreter()