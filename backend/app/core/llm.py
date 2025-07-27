import openai
import requests
import google.generativeai as genai
from app.settings import (
    OPENAI_API_KEY, OPENAI_API_BASE, HUGGINGFACE_API_KEY, GEMINI_API_KEY, 
    LLM_PROVIDER, HUGGINGFACE_DEFAULT_MODEL, CUSTOM_LLM_ENDPOINT, CUSTOM_LLM_API_KEY
)

openai.api_key = OPENAI_API_KEY
openai.base_url = OPENAI_API_BASE

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"  # Model will be appended

def query_llm(prompt: str, model: str = None, temperature: float = 0.2, provider: str = None) -> str:
    # Use provided provider or fallback to environment setting
    current_provider = provider or LLM_PROVIDER
    
    if current_provider == 'custom':
        # Use the custom LLM endpoint
        print(f"Custom LLM endpoint: {CUSTOM_LLM_ENDPOINT}")  # Debug
        
        try:
            # Prepare headers - include API key if provided
            headers = {"Content-Type": "application/json"}
            if CUSTOM_LLM_API_KEY:
                headers["Authorization"] = f"Bearer {CUSTOM_LLM_API_KEY}"
            
            # Prepare payload - adjust based on your endpoint's expected format
            payload = {
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": 512
            }
            
            # Add model parameter if provided
            if model:
                payload["model"] = model
            
            response = requests.post(
                CUSTOM_LLM_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=60  # Increased timeout for custom endpoint
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                raise Exception(f"Custom LLM API error: HTTP {response.status_code} - {response.text}")
            
            # Parse response - adjust based on your endpoint's response format
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, dict):
                if 'response' in data:
                    return data['response'].strip()
                elif 'text' in data:
                    return data['text'].strip()
                elif 'content' in data:
                    return data['content'].strip()
                elif 'result' in data:
                    return data['result'].strip()
                else:
                    # If it's a dict but doesn't have expected keys, return the whole thing as string
                    return str(data).strip()
            elif isinstance(data, str):
                return data.strip()
            else:
                return str(data).strip()
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Custom LLM network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Custom LLM API error: {str(e)}")
    
    elif current_provider == 'openai':
        model = model or "gpt-3.5-turbo"
        print(f"OpenAI base_url: {openai.base_url}, model: {model}")  # Debug
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()
    elif current_provider == 'gemini':
        model = model or "gemini-1.5-flash"
        print(f"Gemini model: {model}")  # Debug
        
        try:
            # Use Gemini Pro for text generation
            gemini_model = genai.GenerativeModel(model)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=512,
                top_p=0.8,
                top_k=40
            )
            
            response = gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    elif current_provider == 'huggingface':
        # Use a default Hugging Face model if the provided model is an OpenAI model name
        openai_models = {"gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"}
        if not model or model in openai_models:
            hf_model = HUGGINGFACE_DEFAULT_MODEL
        else:
            hf_model = model
        
        print(f"Hugging Face model: {hf_model}")  # Debug
        
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        # Different payload format for different model types
        if "flan-t5" in hf_model.lower() or "text2text" in hf_model.lower():
            # Text-to-text models
            payload = {"inputs": prompt}
        else:
            # Text generation models
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 256,
                    "temperature": temperature,
                    "do_sample": True
                }
            }
        
        url = HUGGINGFACE_API_URL + hf_model
        print(f"Making request to: {url}")  # Debug
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Check for HTTP errors
            if resp.status_code == 404:
                raise Exception(f"Model {hf_model} not found or not available for inference")
            elif resp.status_code == 401:
                raise Exception("Invalid Hugging Face API key")
            elif resp.status_code == 429:
                raise Exception("Rate limit exceeded. Try again later.")
            elif resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code}: {resp.text}")
            
            data = resp.json()
            
            # Parse response based on model type
            if isinstance(data, list) and len(data) > 0:
                if 'generated_text' in data[0]:
                    return data[0]['generated_text']
                elif 'translation_text' in data[0]:
                    return data[0]['translation_text']
                else:
                    return str(data[0])
            elif isinstance(data, dict):
                if 'generated_text' in data:
                    return data['generated_text']
                elif 'error' in data:
                    raise Exception(f"Hugging Face API error: {data['error']}")
                else:
                    return str(data)
            else:
                return str(data)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Hugging Face API error: {str(e)}")
    else:
        raise Exception(f"Unsupported LLM_PROVIDER: {current_provider}") 