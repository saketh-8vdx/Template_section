from typing import List, Dict, Any
from langchain.chat_models import ChatOpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langfuse.openai import openai
import os
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.embeddings import BedrockEmbeddings
from concurrent.futures import ThreadPoolExecutor, as_completed
# from final_json import final_josn
import streamlit as st


OPENAI_API_KEY= st.secrets["OPENAI_API_KEY"]
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY




# class PromptGenerator:
#     """Class to generate prompts for financial report sections"""
    
#     def __init__(self):
#         self.llm = ChatOpenAI(
#             model="gpt-4o",
#             temperature=0.1,
#             openai_api_key=OPENAI_API_KEY
#         )
        
#         # Template for generating prompts based on section content
#         self.prompt_template = PromptTemplate(
#             input_variables=["section_name", "contents"],
#             template="""
#             You are an expert financial analyst tasked with creating detailed prompts for generating financial report content.
            
#             Section Name: {section_name}
            
#             The section contains the following content types and examples:
#             {contents}
            
#             Your task is to analyze this section and create specific prompts for each content type that would help generate similar content from other financial documents.
            
#             For each content type, create a detailed prompt that:
#             1. Specifies what information to extract
#             2. Provides context about the section
#             3. Gives clear instructions on format and structure
#             4. Ensures the output matches the original content style
            
#             Return your response as a JSON array with the following structure:
#             [
#                 {{
#                     "type": "content_type_label",
#                     "prompt": "detailed_prompt_for_this_content_type"
#                 }}
#             ]
            
#             Guidelines for different content types:
#             - For "Text" or "paragraph": Create prompts that ask for narrative explanations, analysis, or descriptions
#             - For "Table": Create prompts that ask for structured data, financial metrics, or comparative information
#             - For "List Item": Create prompts that ask for bullet points, key points, or enumerated items
#             - For "Figure": Create prompts that ask for charts, graphs, or visual data representations
#             - For "Title" or "Header": Create prompts that ask for section titles or subtitles
#             - For "Footer": Create prompts that ask for page numbers, dates, or document metadata
            
#             IMPORTANT: Return ONLY the JSON array without any markdown formatting, backticks, or additional text. The response should be parseable JSON.
            
#             Make sure each prompt is specific, actionable, and will generate content that matches the original section's style and depth.
#             """
#         )
        
#         self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
#     def format_contents_for_prompt(self, contents: List[Dict[str, Any]]) -> str:
#         """Format the contents list into a readable string for the prompt"""
#         formatted_contents = []
        
#         for i, content in enumerate(contents, 1):
#             label = content.get("Label", "Unknown")
#             content_text = content.get("Content", "")
            
#             # Truncate content if too long
#             if len(content_text) > 200:
#                 content_text = content_text[:200] + "..."
            
#             formatted_contents.append(f"{i}. Type: {label}\n   Content: {content_text}")
        
#         return "\n".join(formatted_contents)
    
#     def generate_prompt_for_section(self, section_json: Dict[str, Any]) -> List[Dict[str, str]]:
#         """Generate prompts for a single section"""
        
#         section_name = section_json.get("section_header_name", "Unknown Section")
#         contents = section_json.get("Contents", [])
        
#         if not contents:
#             print(f"Warning: No contents found for section '{section_name}'")
#             return []
        
#         # Format contents for the prompt
#         formatted_contents = self.format_contents_for_prompt(contents)
        
#         try:
#             # Generate prompt using LLM
#             result = self.chain.run(
#                 section_name=section_name,
#                 contents=formatted_contents
#             )
            
#             # Clean and parse the JSON response
#             try:
#                 # Remove markdown formatting if present
#                 cleaned_result = result.strip()
#                 if cleaned_result.startswith('```json'):
#                     cleaned_result = cleaned_result[7:]
#                 if cleaned_result.endswith('```'):
#                     cleaned_result = cleaned_result[:-3]
#                 cleaned_result = cleaned_result.strip()
                
#                 prompts = json.loads(cleaned_result)
#                 if isinstance(prompts, list):
#                     return prompts
#                 else:
#                     print(f"Warning: LLM response is not a list for section '{section_name}'")
#                     return []
#             except json.JSONDecodeError as e:
#                 print(f"Error parsing LLM response for section '{section_name}': {e}")
#                 print(f"Raw response: {result}")
#                 return []
                
#         except Exception as e:
#             print(f"Error generating prompt for section '{section_name}': {e}")
#             return []
    
#     def process_final_json(self, final_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Process the entire final JSON and generate prompts for all sections"""
        
#         all_prompts = []
        
#         for i, section_json in enumerate(final_json):
#             print("section_json : ", section_json)
#             print(f"Processing section {i+1}/{len(final_json)}: {section_json.get('section_header_name', 'Unknown')}")
            
#             # Generate prompts for this section
#             section_prompts = self.generate_prompt_for_section(section_json)
            
#             # Create result object for this section in the new format
#             section_result = {
#                 "Section_header": section_json.get("section_header_name", "Unknown"),
#                 "Prompts": section_prompts
#             }
            
#             all_prompts.append(section_result)
            
#             print(f"Generated {len(section_prompts)} prompts for section '{section_json.get('section_header_name', 'Unknown')}'")
        
#         return all_prompts
    
#     def save_results(self, results: List[Dict[str, Any]], output_file: str = "generated_prompts.json"):
#         """Save the generated prompts to a JSON file"""
#         try:
#             with open(output_file, "w") as f:
#                 json.dump(results, f, indent=2)
#             print(f"Results saved to {output_file}")
#         except Exception as e:
#             print(f"Error saving results: {e}")
    
#     def print_summary(self, results: List[Dict[str, Any]]):
#         """Print a summary of the generated prompts"""
#         print("\n" + "="*60)
#         print("PROMPT GENERATION SUMMARY")
#         print("="*60)
        
#         for section_result in results:
#             section_name = section_result["Section_header"]
#             prompt_count = len(section_result["Prompts"])
            
#             print(f"\nSection: {section_name}")
#             print(f"  Generated prompts: {prompt_count}")
            
#             for i, prompt_obj in enumerate(section_result["Prompts"], 1):
#                 prompt_type = prompt_obj.get("type", "Unknown")
#                 prompt_text = prompt_obj.get("prompt", "")
#                 print(f"    {i}. Type: {prompt_type}")
#                 print(f"       Prompt: {prompt_text[:100]}...")




class PromptGenerator:
    """Class to generate prompts for financial report sections"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            openai_api_key=OPENAI_API_KEY
        )

        self.prompt_template = PromptTemplate(
            input_variables=["section_name", "contents"],
            template="""
            You are an expert financial analyst tasked with creating detailed prompts for generating financial report content.

            Section Name: {section_name}

            The section contains the following content types and examples:
            {contents}

            Your task is to analyze this section and create specific prompts for each content type that would help generate similar content from other financial documents.

            For each content type, create a detailed prompt that:
            1. Specifies what information to extract
            2. Provides context about the section
            3. Gives clear instructions on format and structure
            4. Ensures the output matches the original content style

            Return your response as a JSON array with the following structure:
            [
                {{
                    "type": "content_type_label",
                    "prompt": "detailed_prompt_for_this_content_type"
                }}
            ]

            Guidelines for different content types:
            - For "Text" or "paragraph": Create prompts that ask for narrative explanations, analysis, or descriptions
            - For "Table": Create prompts that ask for structured data, financial metrics, or comparative information
            - For "List Item": Create prompts that ask for bullet points, key points, or enumerated items
            - For "Figure": Create prompts that ask for charts, graphs, or visual data representations
            - For "Title" or "Header": Create prompts that ask for section titles or subtitles
            - For "Footer": Create prompts that ask for page numbers, dates, or document metadata

            IMPORTANT: Return ONLY the JSON array without any markdown formatting, backticks, or additional text. The response should be parseable JSON.

            Make sure each prompt is specific, actionable, and will generate content that matches the original section's style and depth.
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def format_contents_for_prompt(self, contents: List[Dict[str, Any]]) -> str:
        formatted_contents = []
        for i, content in enumerate(contents, 1):
            label = content.get("Label", "Unknown")
            content_text = content.get("Content", "")
            if len(content_text) > 200:
                content_text = content_text[:200] + "..."
            formatted_contents.append(f"{i}. Type: {label}\n   Content: {content_text}")
        return "\n".join(formatted_contents)

    def generate_prompt_for_section(self, section_json: Dict[str, Any]) -> Dict[str, Any]:
        section_name = section_json.get("section_header_name", "Unknown Section")
        contents = section_json.get("Contents", [])

        if not contents:
            print(f"Warning: No contents found for section '{section_name}'")
            return {
                "Section_header": section_name,
                "Prompts": []
            }

        formatted_contents = self.format_contents_for_prompt(contents)

        try:
            result = self.chain.run(
                section_name=section_name,
                contents=formatted_contents
            )

            cleaned_result = result.strip()
            if cleaned_result.startswith('```json'):
                cleaned_result = cleaned_result[7:]
            if cleaned_result.endswith('```'):
                cleaned_result = cleaned_result[:-3]
            cleaned_result = cleaned_result.strip()

            try:
                prompts = json.loads(cleaned_result)
                if isinstance(prompts, list):
                    return {
                        "Section_header": section_name,
                        "Prompts": prompts
                    }
                else:
                    print(f"Warning: LLM response is not a list for section '{section_name}'")
                    return {
                        "Section_header": section_name,
                        "Prompts": []
                    }
            except json.JSONDecodeError as e:
                print(f"Error parsing LLM response for section '{section_name}': {e}")
                print(f"Raw response: {result}")
                return {
                    "Section_header": section_name,
                    "Prompts": []
                }

        except Exception as e:
            print(f"Error generating prompt for section '{section_name}': {e}")
            return {
                "Section_header": section_name,
                "Prompts": []
            }

    def process_final_json(self, final_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_prompts = [None] * len(final_json)

        def task(index: int, section: Dict[str, Any]):
            print(f"Processing section {index+1}/{len(final_json)}: {section.get('section_header_name', 'Unknown')}")
            result = self.generate_prompt_for_section(section)
            return index, result

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(task, idx, section_json) for idx, section_json in enumerate(final_json)]

            for future in as_completed(futures):
                idx, section_result = future.result()
                all_prompts[idx] = section_result
                print(f"Generated {len(section_result['Prompts'])} prompts for section '{section_result['Section_header']}'")

        return all_prompts

    def save_results(self, results: List[Dict[str, Any]], output_file: str = "generated_prompts.json"):
        try:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")

    def print_summary(self, results: List[Dict[str, Any]]):
        print("\n" + "="*60)
        print("PROMPT GENERATION SUMMARY")
        print("="*60)

        for section_result in results:
            section_name = section_result["Section_header"]
            prompt_count = len(section_result["Prompts"])

            print(f"\nSection: {section_name}")
            print(f"  Generated prompts: {prompt_count}")

            for i, prompt_obj in enumerate(section_result["Prompts"], 1):
                prompt_type = prompt_obj.get("type", "Unknown")
                prompt_text = prompt_obj.get("prompt", "")
                print(f"    {i}. Type: {prompt_type}")
                print(f"       Prompt: {prompt_text[:100]}...")





# if __name__ == "__main__":
#     # Initialize the prompt generator
#     generator = PromptGenerator()
    
#     # Example final JSON structure (replace with your actual data)
#     example_final_json = [
#         {
#             "section_header_name": "Executive Summary",
#             "Contents": [
#                 {
#                     "Label": "paragraph",
#                     "Content": "This investment memo presents a compelling opportunity to invest in Argano, a leading digital transformation company."
#                 },
#                 {
#                     "Label": "table",
#                     "Content": "Financial Highlights: Revenue: $50M, Growth: 25%, EBITDA: $8M"
#                 },
#                 {
#                     "Label": "list",
#                     "Content": "Key Investment Highlights: Strong market position, Experienced management team, Scalable business model"
#                 }
#             ]
#         },
#         {
#             "section_header_name": "Investment Thesis",
#             "Contents": [
#                 {
#                     "Label": "paragraph",
#                     "Content": "Argano operates in the rapidly growing digital transformation market, which is expected to reach $500B by 2025."
#                 },
#                 {
#                     "Label": "paragraph",
#                     "Content": "The company has demonstrated consistent growth and profitability over the past three years."
#                 }
#             ]
#         }
#     ]

#     print("Starting prompt generation...")
#     results = generator.process_final_json(final_josn)
    
#     # Save results
#     generator.save_results(results, "../../Downloads/ai_analyst_data/generated_prompts1.json")
    
#     # Print summary
#     generator.print_summary(results)
    
#     print("\nPrompt generation completed!")