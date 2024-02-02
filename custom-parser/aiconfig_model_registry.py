from aiconfig import AIConfigRuntime
import requests
import json
from typing import Any, Dict, List, Optional
from aiconfig.callback import CallbackEvent
from aiconfig.Config import AIConfigRuntime
from aiconfig.default_parsers.parameterized_model_parser import (
    ParameterizedModelParser,
)
from aiconfig.model_parser import InferenceOptions
from aiconfig.util.params import resolve_prompt


from aiconfig.schema import AIConfig, ExecuteResult, Output, OutputDataWithValue, Prompt

url = "http://localhost:8000/"

class CustomModelParser(ParameterizedModelParser):
    def __init__(self):
        super().__init__()
        self.qa = []
        
    async def serialize(
        self, 
        prompt_name: str, 
        data: Any, 
        ai_config: AIConfigRuntime, 
        parameters: Dict | None = None, 
        **kwargs
        ) -> List[Prompt]:
            print("serializing")
            event = CallbackEvent(
                "on_serialize_start",
                __name__,
                {
                    "prompt_name" : prompt_name,
                    "data": data,
                    "parameters":parameters,
                    "kwargs" : kwargs
                }
            )
            await ai_config.callback_manager.run_callbacks(event)
            
            
            parameters = parameters or {}
            out = Prompt(name = prompt_name, input = data)
            print(out)
            return [out] 
        
    async def deserialize(self, prompt: Prompt, aiconfig: AIConfig, params: Dict | None = ...) -> Dict:
        resolved = resolve_prompt(prompt, params, aiconfig)
        
        model_input = (
            f"QUESTION:\n{resolved}"
        )
        output_text = self.get_output_text(prompt=prompt, aiconfig=aiconfig)
        
        await aiconfig.callback_manager.run_callbacks(
            CallbackEvent(
                "on_deserialize_complete",
                __name__,
                {"output": {"model_input" : model_input, "output": output_text}},
            )
        )
        
        return {"model_input" : model_input,
                "output": output_text}
    
        
    def id(self) -> str:
        return "Custom"
    
    async def run_inference(
        self,
        prompt: Prompt,
        aiconfig: AIConfigRuntime,
        options: InferenceOptions | None,
        parameters: dict,
    ) -> List[Output]:
        
        resolved = await self.deserialize(prompt, aiconfig, parameters)
        model_input= resolved["model_input"]
        result = await self._run_inference_helper(model_input, options)
        await aiconfig.callback_manager.run_callbacks(
            CallbackEvent(
                "on_run_start",
                __name__,
                {"result": [result]}
            )
        )
        return [result]
    
    
    async def _run_inference_helper(
        self, model_input, options:InferenceOptions
    ) -> List[Output]:
        llm = ""
        acc = ""
        
        stream = options.stream if options else True
        stream = True
        
        response = requests.get(url)
        print(response.json())
        response_json =  response.json()
        results =  response_json['response']
        
        
        # results = [{
        #     "choices":[
        #         {
        #         "text" : "Custom",
        #         "index" : "0"
        #         },
        #     ]},
        #     {
        #     "choices":[
        #         {
        #         "text" : " Model",
        #         "index" : "1"
        #         },
        #     ]}]
        
        if stream:
            for res in results:
                raw_data = res["choices"][0]
                data = raw_data["text"]
                index = int(raw_data["index"])
                acc += data
                if options:
                    options.stream_callback(data, acc, index)
            print(flush=True)

            output_data_value: str = ""
            if isinstance(acc, str):
                output_data_value = acc
            else:
                raise ValueError(
                    f"Output {acc} needs to be of type 'str' but is of type: {type(acc)}"
                )
            return ExecuteResult(
                output_type="execute_result",
                data=output_data_value,
                metadata={},
            )
        else:
            '''
                response = llm(model_input)
            try:
                texts = [r["choices"][0]["text"] for r in response]
            except TypeError:
                texts = [response["choices"][0]["text"]]
            '''
            texts = "Custom Model"
            return ExecuteResult(
                output_type="execute_result",
                data=texts,
                metadata={},
            )
    def get_output_text(
        self,
        prompt: Prompt,
        aiconfig: AIConfigRuntime,
        output: Output | None = None,
    ) -> str:
        print("output_data")
        if not output:
            output = aiconfig.get_latest_output(prompt)

        if not output:
            return ""
        
        if output.output_type == "execute_result":
            
            output_data = output.data
            if isinstance(output_data, str):
                return output_data
            if isinstance(output_data, OutputDataWithValue):
                if isinstance(output_data.value, str):
                    return output_data.value

                return json.dumps(output_data.value, indent=2)
            if isinstance(output_data, list):

                return output_data
            return output_data
        raise ValueError(
            f"Output is an unexpected output type: {type(output)}"
        )
        
from aiconfig.model_parser import InferenceOptions


def register_model_parsers() -> None:
    parser = CustomModelParser()
    AIConfigRuntime.register_model_parser(parser, "Custom")
    
# if __name__ == '__main__':
#     register_model_parsers()
    