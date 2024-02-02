import { PromptSchema } from "../../utils/promptUtils";

export const GoogleSearchPromptSchema: PromptSchema = {
  // https://platform.openai.com/docs/api-reference/chat/create
  input: {
    type: "string",
  },
  model_settings: {
    type: "object",
    properties: {
      model: {
        type: "string",
      },
      exclude_terms: {
        type: "string",
      },
      number_of_results: {
        type: "number",
        minimum: 0,
        maximum: 50,
        description: `Number between 0 and 50. 
        Gives the number of top results to return as outptut`,
      },
    },
  },
  prompt_metadata: {
    type: "object",
    properties: {
      remember_chat_context: {
        type: "boolean",
      },
    },
  },
};
