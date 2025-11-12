from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import requests
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# E-commerce focused system prompt
SYSTEM_PROMPT = """You are a professional e-commerce customer service assistant. Your role is to:

1. Help customers find products they're looking for on e-commerce platforms (Flipkart, Amazon, etc.)
2. Provide detailed product information (features, specifications, pricing)
3. Answer questions about products, shipping, returns, and policies
4. Assist with product recommendations based on customer needs
5. Handle customer inquiries professionally

IMPORTANT: 
- Focus ONLY on e-commerce products and shopping assistance
- When products are found, provide helpful information about them
- Always be friendly, helpful, and professional
- If asked about non-e-commerce topics, politely redirect to product-related questions"""

# Configure DeepSeek API
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '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')
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek/deepseek-chat-v3.1:free")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.skylark.com/v1")
USE_DEEPSEEK = False

# DeepSeek generation config
deepseek_config = {
    "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("DEEPSEEK_MAX_TOKENS", "1024")),
}

if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY.strip():
    USE_DEEPSEEK = True
    print(f"✓ DeepSeek API configured")
    print(f"  Model: {DEEPSEEK_MODEL}")
    print(f"  API Base: {DEEPSEEK_API_BASE}")
    print(f"  API Key: {DEEPSEEK_API_KEY[:20]}...{DEEPSEEK_API_KEY[-10:]}")
else:
    print("ℹ Using free product search APIs (no API key required)")
    USE_DEEPSEEK = False

# HTTP headers for scraping e-commerce sites
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def search_products_duckduckgo(query):
    """Search for products using DuckDuckGo (free, no API key required)"""
    try:
        # DuckDuckGo Instant Answer API (completely free)
        ddg_url = f"https://api.duckduckgo.com/?q={quote(query + ' buy online')}&format=json&no_html=1"
        response = requests.get(ddg_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # DuckDuckGo provides related topics which we can use
            if data.get('RelatedTopics'):
                products = []
                for topic in data['RelatedTopics'][:5]:
                    if 'Text' in topic:
                        text = topic['Text']
                        # Extract product name and create search links
                        product_name = text.split(' - ')[0] if ' - ' in text else query
                        products.append({
                            "name": product_name[:100],
                            "price": "Check website",
                            "description": text[:200] if len(text) > 200 else text,
                            "image": topic.get('Icon', {}).get('URL', '') or f"https://via.placeholder.com/300x300/667eea/ffffff?text={quote(product_name[:20])}",
                            "flipkart_link": f"https://www.flipkart.com/search?q={quote(product_name)}",
                            "amazon_link": f"https://www.amazon.in/s?k={quote(product_name)}",
                            "rating": "4.0+",
                            "source": "DuckDuckGo",
                            "inStock": True
                        })
                if products:
                    return products
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
    return None

def search_products_web(query):
    """Search for products using web scraping (free, no API key)"""
    try:
        # Use a product search approach
        # Create product suggestions based on common e-commerce patterns
        query_lower = query.lower()
        
        # Extract price range
        price_range = ""
        price_match = re.search(r'(\d+)[-\s]*(\d+)?\s*k', query_lower)
        if price_match:
            min_price = price_match.group(1)
            max_price = price_match.group(2) if price_match.group(2) else str(int(min_price) + 5)
            price_range = f"₹{min_price},000 - ₹{max_price},000"
        
        # Product templates for common searches
        product_templates = {
            'watch': [
                {'name': 'Seiko 5 Sports Automatic SRPD Series', 'price': '₹15,000 - ₹25,000', 'rating': '4.5',
                 'desc': 'A highly regarded automatic watch known for its reliability and value. It features a robust in-house automatic movement, a day-date display, and a see-through case back. Its versatile design makes it suitable for both casual and semi-formal occasions.'},
                {'name': 'Tissot PRX Quartz', 'price': '₹20,000 - ₹30,000', 'rating': '4.6',
                 'desc': 'A stunning Swiss-made watch featuring a timeless 1970s integrated bracelet design. It comes with a high-quality quartz movement, a scratch-resistant sapphire crystal, and a beautifully finished case that exudes premium quality.'},
                {'name': 'Fossil Gen 6 Smartwatch', 'price': '₹18,000 - ₹25,000', 'rating': '4.4',
                 'desc': 'Feature-rich smartwatch with fitness tracking, notifications, and Google Wear OS. Perfect for active lifestyles and tech enthusiasts who want style and functionality.'},
            ],
            'headphone': [
                {'name': 'Sony WH-1000XM4 Wireless Headphones', 'price': '₹25,000 - ₹30,000', 'rating': '4.7',
                 'desc': 'Premium noise-cancelling headphones with exceptional sound quality. Features 30-hour battery life and industry-leading ANC technology for immersive listening experience.'},
                {'name': 'Bose QuietComfort 45', 'price': '₹28,000 - ₹35,000', 'rating': '4.6',
                 'desc': 'Comfortable over-ear headphones with excellent noise cancellation. Known for superior comfort during long listening sessions and crystal-clear audio.'},
                {'name': 'JBL Tune 760NC', 'price': '₹5,000 - ₹8,000', 'rating': '4.3',
                 'desc': 'Affordable wireless headphones with active noise cancellation. Great value for money with good sound quality and comfortable fit.'},
            ],
            'laptop': [
                {'name': 'HP Pavilion 15', 'price': '₹45,000 - ₹60,000', 'rating': '4.4',
                 'desc': 'Reliable laptop for everyday computing tasks. Features modern processors, good display, and solid build quality perfect for students and professionals.'},
                {'name': 'Dell Inspiron 15', 'price': '₹50,000 - ₹65,000', 'rating': '4.5',
                 'desc': 'Versatile laptop suitable for work and entertainment. Known for durability and excellent customer support with good performance.'},
            ],
            'phone': [
                {'name': 'Samsung Galaxy S23', 'price': '₹60,000 - ₹80,000', 'rating': '4.6',
                 'desc': 'Flagship smartphone with excellent camera system and powerful performance. Premium design and display quality with long-lasting battery.'},
                {'name': 'OnePlus 11', 'price': '₹50,000 - ₹65,000', 'rating': '4.5',
                 'desc': 'High-performance smartphone with fast charging and smooth user experience. Great for gaming and photography enthusiasts.'},
            ],
        }
        
        # Find matching product type
        products = []
        for key, templates in product_templates.items():
            if key in query_lower:
                products = templates
                break
        
        # If no match, create generic products
        if not products:
            products = [
                {'name': f'{query.title()} - Premium Option', 'price': price_range or 'Check website', 'rating': '4.5',
                 'desc': f'High-quality {query} option with excellent features and customer satisfaction. Available on major e-commerce platforms with secure payment and reliable delivery.'},
                {'name': f'{query.title()} - Standard Option', 'price': price_range or 'Check website', 'rating': '4.3',
                 'desc': f'Well-balanced {query} option offering great value. Popular choice among customers with positive reviews and good build quality.'},
            ]
        
        # Format products with links and images
        formatted_products = []
        for product in products[:5]:
            product_name = product['name']
            # Try to get product image from Unsplash or use placeholder
            image_url = f"https://source.unsplash.com/400x400/?{quote(product_name.split()[0] if product_name.split() else query)}"
            
            formatted_products.append({
                'name': product_name,
                'price': product['price'],
                'description': product['desc'],
                'rating': product['rating'],
                'flipkart_link': f"https://www.flipkart.com/search?q={quote(product_name)}",
                'amazon_link': f"https://www.amazon.in/s?k={quote(product_name)}",
                'image': image_url,
                'inStock': True,
                'source': 'Curated'
            })
        
        return formatted_products
        
    except Exception as e:
        print(f"Web search error: {e}")
        return None


def _normalize_price(text):
    if not text:
        return "Check website"
    cleaned = re.sub(r"[^\d.,₹$]", "", text)
    if cleaned:
        if cleaned.startswith("₹"):
            return cleaned if "₹" in text else f"₹{cleaned}"
        if cleaned.startswith("$"):
            return cleaned
        return f"₹{cleaned}"
    return "Check website"


def scrape_flipkart_products(query, limit=5):
    """Fetch product listings directly from Flipkart search results."""
    try:
        params = {"q": query, "otracker": "search"}
        response = requests.get(
            "https://www.flipkart.com/search",
            params=params,
            headers=DEFAULT_HEADERS,
            timeout=10,
        )
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        product_cards = soup.select("a._1fQZEK")  # Grid layout
        if not product_cards:
            product_cards = soup.select("a.s1Q9rs")  # List layout (e.g. fashion)
        if not product_cards:
            product_cards = soup.select("div._4ddWXP a.s1Q9rs")  # Alternate layout

        products = []
        seen_names = set()

        for anchor in product_cards:
            name = anchor.get_text(strip=True)
            if not name or name in seen_names:
                continue

            seen_names.add(name)
            href = anchor.get("href")
            product_url = urljoin("https://www.flipkart.com", href) if href else ""

            card_root = anchor
            for _ in range(3):
                if card_root and card_root.name != "div":
                    card_root = card_root.parent

            price_tag = (
                card_root.select_one("div._30jeq3") if card_root else None
            ) or anchor.find_next("div", class_="_30jeq3")

            rating_tag = (
                card_root.select_one("div._3LWZlK") if card_root else None
            ) or anchor.find_next("div", class_="_3LWZlK")

            image_tag = (
                card_root.select_one("img") if card_root else None
            ) or anchor.find_next("img")
            image_url = ""
            if image_tag:
                image_url = image_tag.get("src") or image_tag.get("data-src") or ""
                if image_url.startswith("//"):
                    image_url = "https:" + image_url

            description = ""
            if card_root:
                bullets = card_root.select("ul._1xgFaf li")
                if bullets:
                    description = "; ".join(b.get_text(strip=True) for b in bullets[:3])

            products.append(
                {
                    "name": name,
                    "price": _normalize_price(price_tag.get_text() if price_tag else ""),
                    "rating": rating_tag.get_text(strip=True) if rating_tag else "4.0",
                    "description": description
                    or "Top listing from Flipkart curated for your search.",
                    "image": image_url,
                    "flipkart_link": product_url,
                    "amazon_link": "",
                    "source": "Flipkart",
                    "inStock": True,
                }
            )

            if len(products) >= limit:
                break

        return products
    except Exception as exc:
        print(f"Flipkart scrape error: {exc}")
        return []


def scrape_amazon_products(query, limit=5):
    """Fetch product listings directly from Amazon search results."""
    try:
        params = {"k": query, "ref": "nb_sb_noss"}
        response = requests.get(
            "https://www.amazon.in/s",
            params=params,
            headers={
                **DEFAULT_HEADERS,
                "Accept-Encoding": "gzip, deflate, br",
            },
            timeout=10,
        )
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        result_cards = soup.select('div.s-main-slot div[data-component-type="s-search-result"]')

        products = []
        seen_names = set()

        for card in result_cards:
            title_tag = card.select_one("h2 a span")
            if not title_tag:
                continue
            name = title_tag.get_text(strip=True)
            if not name or name in seen_names:
                continue
            seen_names.add(name)

            link_tag = card.select_one("h2 a")
            product_url = (
                urljoin("https://www.amazon.in", link_tag.get("href"))
                if link_tag and link_tag.get("href")
                else ""
            )

            price_whole = card.select_one("span.a-price span.a-price-whole")
            price_fraction = card.select_one("span.a-price span.a-price-fraction")
            price_text = ""
            if price_whole:
                price_text = price_whole.get_text(strip=True)
                if price_fraction:
                    price_text += price_fraction.get_text(strip=True)

            rating_tag = card.select_one("span.a-icon-alt")
            image_tag = card.select_one("img.s-image")
            image_url = ""
            if image_tag:
                image_url = image_tag.get("src") or image_tag.get("data-src") or ""
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
            description = ""

            bullets = card.select("div.a-section.a-spacing-small.a-spacing-top-small span.a-text-normal")
            if bullets:
                description = " ".join(b.get_text(strip=True) for b in bullets[:2])

            products.append(
                {
                    "name": name,
                    "price": _normalize_price(price_text),
                    "rating": rating_tag.get_text(strip=True).split()[0] if rating_tag else "4.0",
                    "description": description or "Popular Amazon listing tailored to your request.",
                    "image": image_url,
                    "flipkart_link": "",
                    "amazon_link": product_url,
                    "source": "Amazon",
                    "inStock": True,
                }
            )

            if len(products) >= limit:
                break

        return products
    except Exception as exc:
        print(f"Amazon scrape error: {exc}")
        return []

def search_real_products(query):
    """Search for real products using free APIs (no API key required)"""
    # Try direct marketplace scraping first for higher accuracy
    flipkart_products = scrape_flipkart_products(query, limit=4)
    amazon_products = scrape_amazon_products(query, limit=4)

    combined_products = []
    seen_names = set()

    for product in flipkart_products + amazon_products:
        key = (product["name"], product.get("source"))
        if key in seen_names:
            continue
        seen_names.add(key)
        # Ensure both marketplace links exist where possible
        if product.get("source") == "Flipkart" and not product.get("amazon_link"):
            product["amazon_link"] = f"https://www.amazon.in/s?k={quote(product['name'])}"
        if product.get("source") == "Amazon" and not product.get("flipkart_link"):
            product["flipkart_link"] = f"https://www.flipkart.com/search?q={quote(product['name'])}"
        combined_products.append(product)

    if combined_products:
        return combined_products

    # Try DuckDuckGo first (completely free)
    products = search_products_duckduckgo(query)
    if products:
        return products
    
    # Fallback to web-based product search
    products = search_products_web(query)
    if products:
        return products
    
    # Ultimate fallback
    return create_fallback_products(query)

def generate_template_response(user_message, products):
    """Generate a helpful response without using paid APIs"""
    if products:
        response = f"Great! I found some excellent options for '{user_message}':\n\n"
        for i, product in enumerate(products[:3], 1):
            response += f"**{product.get('name', 'Product')}**\n"
            response += f"Price: {product.get('price', 'Check website')}\n"
            response += f"Rating: {product.get('rating', 'N/A')} ⭐\n"
            if product.get("source"):
                response += f"Source: {product['source']}\n"
            response += f"{product.get('description', '')}\n\n"
        response += "💡 **Tip:** Click the 'Buy on Flipkart' or 'Buy on Amazon' buttons below each product to view more details, compare prices, and make a purchase!\n\n"
        response += "All products come with secure payment options and reliable delivery. Happy shopping! 🛍️"
    else:
        response = f"I'd be happy to help you find the best '{user_message}' options!\n\n"
        response += "Please try searching with more specific terms, or browse our product categories. "
        response += "You can click on the product links to explore options on Flipkart and Amazon.\n\n"
        response += "How else can I assist you today? 😊"
    
    return response


def generate_deepseek_response(user_message, products):
    """Create a DeepSeek-powered response when API access is available."""
    if not USE_DEEPSEEK or not DEEPSEEK_API_KEY:
        print("⚠ DeepSeek not available - USE_DEEPSEEK:", USE_DEEPSEEK, "API_KEY exists:", bool(DEEPSEEK_API_KEY))
        return None

    try:
        print(f"🔄 Calling DeepSeek API with model: {DEEPSEEK_MODEL}")
        product_context = []
        for idx, product in enumerate(products[:5], start=1):
            product_context.append(
                f"""{idx}. {product.get('name', 'Product')}
   Price: {product.get('price', 'Check website')}
   Rating: {product.get('rating', 'N/A')}
   Description: {product.get('description', 'No description available')}
   Flipkart: {product.get('flipkart_link', 'N/A')}
   Amazon: {product.get('amazon_link', 'N/A')}"""
            )

        product_block = "\n".join(product_context) if product_context else "No exact matches found yet."

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "User query:\n"
                    f"{user_message}\n\n"
                    "Product findings from live marketplace searches:\n"
                    f"{product_block}\n\n"
                    "Compose a concise, customer-friendly reply that:\n"
                    "1. Recommends the most relevant options.\n"
                    "2. Highlights differentiators, pricing, and availability hints.\n"
                    "3. Encourages the shopper to review the provided Flipkart/Amazon links.\n"
                    "4. Offers next-step guidance or alternative suggestions if needed.\n"
                )
            }
        ]

        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": deepseek_config["temperature"],
            "max_tokens": deepseek_config["max_tokens"],
        }

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }

        api_url = f"{DEEPSEEK_API_BASE}/chat/completions"
        print(f"📡 API URL: {api_url}")
        
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=30,
        )

        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response received: {list(result.keys())}")
            if "error" in result:
                print(f"❌ DeepSeek API error in response: {result.get('error', {})}")
                return None
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                if content:
                    print(f"✅ DeepSeek response generated successfully ({len(content)} chars)")
                    return content.strip()
                else:
                    print("⚠️ No content in API response choices")
            else:
                print(f"⚠️ No choices in API response. Response keys: {list(result.keys())}")
        else:
            try:
                error_data = response.json()
                print(f"❌ DeepSeek API error: {response.status_code} - {error_data}")
            except:
                print(f"❌ DeepSeek API error: {response.status_code} - {response.text[:200]}")

    except Exception as exc:
        error_msg = str(exc).lower()
        if "429" in error_msg or "quota" in error_msg:
            print("⚠ DeepSeek quota exceeded, switching to template response.")
        else:
            print(f"DeepSeek response error: {exc}")

    return None

def create_fallback_products(query):
    """Create fallback product results with search links"""
    products = []
    query_encoded = quote(query)
    
    # Create 3 product suggestions with search links
    for i in range(3):
        products.append({
            "name": f"{query.title()} - Option {i+1}",
            "price": "Check website",
            "description": f"Find the best {query} options on e-commerce platforms. Browse through various models and compare prices.",
            "image": f"https://source.unsplash.com/400x400/?{quote(query)}",
            "flipkart_link": f"https://www.flipkart.com/search?q={query_encoded}",
            "amazon_link": f"https://www.amazon.in/s?k={query_encoded}",
            "rating": "4.0+",
            "inStock": True,
            "source": "Search"
        })
    
    return products

# Legacy product database (kept for backward compatibility, but not used)
PRODUCTS = [
    {
        "id": 1,
        "name": "Wireless Bluetooth Headphones",
        "price": 79.99,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        "category": "Electronics",
        "description": "Premium noise-cancelling wireless headphones with 30-hour battery life",
        "rating": 4.5,
        "inStock": True
    },
    {
        "id": 2,
        "name": "Smart Watch Pro",
        "price": 249.99,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
        "category": "Electronics",
        "description": "Advanced fitness tracking smartwatch with heart rate monitor and GPS",
        "rating": 4.7,
        "inStock": True
    },
    {
        "id": 3,
        "name": "Laptop Backpack",
        "price": 49.99,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
        "category": "Accessories",
        "description": "Durable laptop backpack with USB charging port and water-resistant material",
        "rating": 4.3,
        "inStock": True
    },
    {
        "id": 4,
        "name": "Wireless Mouse",
        "price": 29.99,
        "image": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=400",
        "category": "Electronics",
        "description": "Ergonomic wireless mouse with precision tracking and long battery life",
        "rating": 4.4,
        "inStock": True
    },
    {
        "id": 5,
        "name": "Mechanical Keyboard",
        "price": 129.99,
        "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400",
        "category": "Electronics",
        "description": "RGB backlit mechanical keyboard with Cherry MX switches",
        "rating": 4.6,
        "inStock": True
    },
    {
        "id": 6,
        "name": "USB-C Hub",
        "price": 39.99,
        "image": "https://images.unsplash.com/photo-1625842268584-8f7623b58d85?w=400",
        "category": "Accessories",
        "description": "7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader",
        "rating": 4.2,
        "inStock": True
    },
    {
        "id": 7,
        "name": "Phone Stand",
        "price": 19.99,
        "image": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400",
        "category": "Accessories",
        "description": "Adjustable aluminum phone stand for desk and car use",
        "rating": 4.1,
        "inStock": True
    },
    {
        "id": 8,
        "name": "Wireless Charger",
        "price": 24.99,
        "image": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400",
        "category": "Electronics",
        "description": "Fast wireless charging pad compatible with all Qi-enabled devices",
        "rating": 4.5,
        "inStock": True
    },
    {
        "id": 9,
        "name": "Fitness Watch Elite",
        "price": 199.99,
        "image": "https://images.unsplash.com/photo-1579586337278-3befd40f17ca?w=400",
        "category": "Electronics",
        "description": "Premium fitness smartwatch with advanced health monitoring and 10-day battery",
        "rating": 4.6,
        "inStock": True
    },
    {
        "id": 10,
        "name": "Sport Watch Active",
        "price": 179.99,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
        "category": "Electronics",
        "description": "Rugged sports watch with GPS, heart rate monitor, and 14-day battery life",
        "rating": 4.4,
        "inStock": True
    },
    {
        "id": 11,
        "name": "Classic Smart Watch",
        "price": 229.99,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
        "category": "Electronics",
        "description": "Elegant smartwatch with premium design, AMOLED display, and comprehensive health tracking",
        "rating": 4.8,
        "inStock": True
    }
]

def search_products_legacy(query):
    """Search products by name, category, or description with improved matching"""
    query_lower = query.lower()
    results = []
    
    # Create synonym mapping for better search
    synonyms = {
        'watch': ['watch', 'smartwatch', 'smart watch', 'timepiece', 'wristwatch'],
        'headphone': ['headphone', 'headphones', 'earphone', 'earphones', 'audio'],
        'mouse': ['mouse', 'computer mouse', 'wireless mouse'],
        'keyboard': ['keyboard', 'mechanical keyboard', 'keyboard'],
        'backpack': ['backpack', 'bag', 'laptop bag', 'rucksack'],
        'charger': ['charger', 'wireless charger', 'charging'],
        'hub': ['hub', 'usb hub', 'adapter']
    }
    
    # Extract price range if mentioned (e.g., "20-25k", "$200-$250")
    price_min = None
    price_max = None
    if 'k' in query_lower or 'thousand' in query_lower:
        # Handle "20-25k" format (assuming INR, convert to USD: 1 USD ≈ 83 INR)
        price_match = re.search(r'(\d+)[-\s]*(\d+)?\s*k', query_lower)
        if price_match:
            inr_min = float(price_match.group(1)) * 1000
            if price_match.group(2):
                inr_max = float(price_match.group(2)) * 1000
            else:
                inr_max = inr_min + 5000  # Add 5k range
            # Convert INR to USD (approximate: 1 USD = 83 INR)
            price_min = inr_min / 83
            price_max = inr_max / 83
    elif '$' in query:
        # Handle "$200-$250" format
        price_matches = re.findall(r'\$(\d+)', query)
        if len(price_matches) >= 1:
            price_min = float(price_matches[0])
            if len(price_matches) >= 2:
                price_max = float(price_matches[1])
            else:
                price_max = price_min + 50
    
    for product in PRODUCTS:
        score = 0
        product_text = f"{product['name']} {product['category']} {product['description']}".lower()
        
        # Direct match
        if query_lower in product_text:
            score += 10
        
        # Synonym matching
        for key, values in synonyms.items():
            if any(syn in query_lower for syn in values):
                if key in product_text:
                    score += 8
        
        # Word-by-word matching
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 2 and word in product_text:
                score += 2
        
        # Price range filtering (with some flexibility)
        if price_min is not None and price_max is not None:
            # Allow 10% flexibility in price range
            price_tolerance = (price_max - price_min) * 0.1
            if not (price_min - price_tolerance <= product['price'] <= price_max + price_tolerance):
                continue
        
        if score > 0:
            product['match_score'] = score
            results.append(product)
    
    # Sort by match score (highest first)
    results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    # Remove match_score before returning
    for product in results:
        product.pop('match_score', None)
    
    return results

def format_product_response(products, user_message):
    """Format product information for the AI response"""
    if not products:
        return None
    
    product_info = "\n\nAvailable Products:\n"
    for product in products[:3]:  # Limit to 3 products
        product_info += f"- {product['name']} (${product['price']}) - {product['description']}\n"
    
    return product_info

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products or search products"""
    query = request.args.get('q', '').strip()
    if query:
        results = search_real_products(query)
        return jsonify({'products': results})
    return jsonify({'products': []})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        # Search for real products on e-commerce sites
        found_products = search_real_products(user_message)
        print(f"User query: {user_message}")
        print(f"Found {len(found_products)} products")
        if found_products:
            print(f"Products: {[p['name'] for p in found_products]}")
        
        # Generate response (use DeepSeek if available, otherwise use template)
        response_text = None
        if USE_DEEPSEEK:
            response_text = generate_deepseek_response(user_message, found_products)

        if not response_text:
            # Use free template response
            response_text = generate_template_response(user_message, found_products)
        
        # Check if user is asking about non-e-commerce topics
        non_ecommerce_keywords = ['weather', 'news', 'sports', 'politics', 'general knowledge', 'history', 'science']
        if any(keyword in user_message.lower() for keyword in non_ecommerce_keywords):
            response_text = "I'm here to help you find products on e-commerce platforms like Flipkart and Amazon. How can I assist you with finding products today?"
            return jsonify({
                'response': response_text,
                'products': []
            })
        
        return jsonify({
            'response': response_text,
            'products': found_products[:5] if found_products else []
        })
            
    except Exception as e:
        error_message = str(e)
        print(f"Error in chat endpoint: {error_message}")
        
        # Check for quota exceeded error
        if '429' in error_message or 'quota' in error_message.lower() or 'Quota exceeded' in error_message:
            return jsonify({
                'response': '⚠️ API Quota Exceeded: You have reached the free tier limit (2 requests). Please wait a few minutes and try again, or use a different API key with higher limits.',
                'error': 'quota_exceeded',
                'products': []
            }), 200
        # Check for API key errors
        elif '401' in error_message or '403' in error_message or 'API key' in error_message:
            return jsonify({
                'response': '⚠️ API Key Error: Please check your DeepSeek API key in the .env file.',
                'error': 'api_key_error',
                'products': []
            }), 200
        # Generic error
        else:
            return jsonify({
                'response': f'Sorry, I could not process your request. Error: {error_message[:100]}',
                'error': 'generic_error',
                'products': []
            }), 200

if __name__ == '__main__':
    app.run(debug=True) 