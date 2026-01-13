"""Content normalizer and cleaner for scraped data."""
import re
from bs4 import BeautifulSoup


def clean_html(html_content: str) -> str:
    """
    Clean HTML content and extract readable text.
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        Cleaned text content
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove unwanted elements
    for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 
                               'aside', 'iframe', 'noscript', 'form']):
        tag.decompose()
    
    # Remove elements by common class names
    unwanted_classes = [
        'navigation', 'nav', 'menu', 'sidebar', 'footer', 'header',
        'comment', 'comments', 'social', 'share', 'related', 'advertisement',
        'ads', 'banner', 'cookie', 'popup'
    ]
    
    for class_name in unwanted_classes:
        for element in soup.find_all(class_=lambda x: x and class_name in x.lower()):
            element.decompose()
    
    # Get text
    text = soup.get_text(separator='\n', strip=True)
    
    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def extract_article_content(html_content: str) -> dict:
    """
    Extract article content with structure.
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        Dict with title, content, and metadata
    """
    if not html_content:
        return {"title": "", "content": "", "excerpt": ""}
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Extract title
    title = ""
    title_tag = soup.find('h1') or soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)
    
    # Try to find main content area
    content_selectors = [
        {'class_': 'entry-content'},
        {'class_': 'post-content'},
        {'class_': 'article-content'},
        {'class_': 'content'},
        {'id': 'content'},
        'article',
        'main',
    ]
    
    main_content = None
    for selector in content_selectors:
        if isinstance(selector, dict):
            main_content = soup.find(**selector)
        else:
            main_content = soup.find(selector)
        if main_content:
            break
    
    if not main_content:
        main_content = soup.find('body') or soup
    
    # Clean the main content
    content_text = clean_html(str(main_content))
    
    # Generate excerpt
    excerpt = content_text[:500] + "..." if len(content_text) > 500 else content_text
    
    return {
        "title": title,
        "content": content_text,
        "excerpt": excerpt
    }


def normalize_arabic_text(text: str) -> str:
    """
    Normalize Arabic text for consistency.
    
    Args:
        text: Text potentially containing Arabic
        
    Returns:
        Normalized text
    """
    # Normalize common Arabic characters
    replacements = {
        'أ': 'ا',
        'إ': 'ا', 
        'آ': 'ا',
        'ة': 'ه',
        'ى': 'ي',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text
