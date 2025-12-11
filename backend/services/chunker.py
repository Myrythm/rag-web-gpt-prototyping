from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):

    # Define headers to split on
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    # First pass: split by markdown headers
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False  # Keep headers in chunks for context
    )
    
    # Second pass: split large chunks by character count
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    # Split by headers first
    md_header_splits = markdown_splitter.split_text(text)
    
    # Then split each section if too large
    final_chunks = []
    for doc in md_header_splits:
        content = doc.page_content
        if len(content) > chunk_size:
            # Split large sections further
            sub_chunks = text_splitter.split_text(content)
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(content)
    
    # If no markdown headers found, fallback to regular splitting
    if not final_chunks:
        final_chunks = text_splitter.split_text(text)
    
    return final_chunks
