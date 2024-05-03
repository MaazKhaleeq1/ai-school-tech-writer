import os
from fetch_release_notes_data import fetch_release_notes_data
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

def main():
    release_notes_data = fetch_release_notes_data('v24.02.00', 'v24.02.01')

    prompt = (
        "Please review the following code changes and commit messages and generate release notes for new version:\n"
        f"{release_notes_data}\n"
        "Consider the code changes and commit messages, compare the given Lithium Operator Manuals and highlight any behavioral change.\n"
    )

    # Note: we must use the same embedding model that we used when uploading the docs
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # Querying the vector database for "relevant" docs
    document_vectorstore = PineconeVectorStore(index_name="lithium-manuals", embedding=embeddings)
    retriever = document_vectorstore.as_retriever()
    context = retriever.get_relevant_documents(prompt)

    # Adding context to our prompt
    template = PromptTemplate(template="{query} Context: {context}", input_variables=["query", "context"])
    prompt_with_context = template.invoke({"query": prompt, "context": context})

    # Asking the LLM for a response from our prompt with the provided context
    llm = ChatOpenAI(temperature=0.7, model='gpt-4-turbo-2024-04-09')
    results = llm.invoke(prompt_with_context)

    print(results.content)

if __name__ == '__main__':
    main()
