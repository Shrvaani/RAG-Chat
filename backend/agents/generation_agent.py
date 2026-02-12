"""Generation Agent - Generates responses using retrieved context."""

from typing import List, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_huggingface import HuggingFaceEndpoint
from backend.config import settings
from backend.agents.state import AgentState


class GenerationAgent:
    """
    Generates responses using LLM with retrieved context.
    """
    
    def __init__(self):
        """Initialize generation agent."""
        self.llm = None
        if settings.huggingface_api_key:
            self.llm = HuggingFaceEndpoint(
                repo_id=settings.hf_model_name,
                huggingfacehub_api_token=settings.huggingface_api_key,
                temperature=0.3,
                max_new_tokens=1024,
                task="text-generation"
            )
    
    async def generate(self, state: AgentState) -> AgentState:
        """
        Generate response and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with generated response
        """
        query = state["query"]
        chunks = state.get("reranked_chunks", [])
        web_results = state.get("web_results", [])
        
        # Add processing step
        state["processing_steps"].append("generation")
        
        if not self.llm:
            # Fallback without LLM
            state["generated_response"] = self._fallback_response(query, chunks, web_results)
            return state
        
        print(f"🤖 Generating response...")
        
        # Build context from chunks
        context = self._build_context(chunks, web_results)
        
        # Generate response
        response = await self._llm_generate(query, context)
        
        state["generated_response"] = response
        print(f"   ✅ Response generated ({len(response)} chars)")
        
        return state
    
    def _build_context(self, chunks: List[Dict], web_results: List[Dict]) -> str:
        """Build context string from retrieved documents."""
        context_parts = []
        
        # Add document chunks
        if chunks:
            context_parts.append("=== Retrieved Documents ===\n")
            for i, chunk in enumerate(chunks[:5], 1):  # Top 5 chunks
                filename = chunk.get('metadata', {}).get('filename', 'Unknown')
                page = chunk.get('metadata', {}).get('page_number')
                content = chunk.get('content', '')
                
                source_info = f"[Source {i}: {filename}"
                if page:
                    source_info += f", Page {page}"
                source_info += "]"
                
                context_parts.append(f"{source_info}\n{content}\n")
        
        # Add web results
        if web_results:
            context_parts.append("\n=== Web Search Results ===\n")
            for i, result in enumerate(web_results[:3], 1):  # Top 3 web results
                title = result.get('title', 'Unknown')
                snippet = result.get('snippet', '')
                url = result.get('url', '')
                
                context_parts.append(f"[Web {i}: {title}]\n{snippet}\nURL: {url}\n")
        
        return "\n".join(context_parts)
    
    async def _llm_generate(self, query: str, context: str) -> str:
        """Generate response using LLM."""
        
        system_prompt = """You are a helpful AI assistant that answers questions based on provided context.

Guidelines:
1. Answer the question using ONLY the information from the provided context
2. If the context doesn't contain enough information, say so clearly
3. Be concise but comprehensive
4. Use specific details and quotes from the context when relevant
5. Maintain a professional, informative tone"""
        
        user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.strip()
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return f"I apologize, but I encountered an error generating a response: {str(e)}"
    
    def _fallback_response(self, query: str, chunks: List[Dict], web_results: List[Dict]) -> str:
        """Fallback response without LLM."""
        if not chunks and not web_results:
            return "I don't have enough information to answer your question."
        
        response_parts = [f"Based on the available information regarding '{query}':\n"]
        
        if chunks:
            response_parts.append(f"\nFrom documents ({len(chunks)} relevant sections found):")
            for i, chunk in enumerate(chunks[:3], 1):
                content = chunk.get('content', '')[:200]
                response_parts.append(f"\n{i}. {content}...")
        
        if web_results:
            response_parts.append(f"\n\nFrom web search ({len(web_results)} results):")
            for i, result in enumerate(web_results[:2], 1):
                snippet = result.get('snippet', '')[:150]
                response_parts.append(f"\n{i}. {snippet}...")
        
        return "\n".join(response_parts)
