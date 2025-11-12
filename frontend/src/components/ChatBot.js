import React, { useState, useRef, useEffect } from 'react';
import './ChatBot.css';
import axios from 'axios';

const ChatBot = () => {
    const [messages, setMessages] = useState([
        {
            text: "👋 Hello! I'm your e-commerce customer service assistant. I can help you find products, answer questions about orders, and assist with any shopping needs. How can I help you today?",
            sender: 'bot',
            timestamp: new Date()
        }
    ]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const formatResponse = (text) => {
        if (text.includes('\n1.') || text.includes('\n•')) {
            return text;
        } else {
            return text.split('\n\n').map(paragraph => paragraph.trim()).join('\n\n');
        }
    };

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) return;

        const userMessage = {
            text: inputMessage,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            // Use environment variable for API URL, fallback to localhost for development
            const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
            const result = await axios.post(`${API_URL}/api/chat`, {
                message: inputMessage
            }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const botMessage = {
                text: formatResponse(result.data.response),
                sender: 'bot',
                timestamp: new Date(),
                products: result.data.products || []
            };
            setMessages(prev => [...prev, botMessage]);
            setError('');
        } catch (err) {
            console.error('Error:', err);
            let errorText = "Sorry, I couldn't process your request. Please try again.";
            
            // Check if the response contains error information
            if (err.response && err.response.data && err.response.data.response) {
                errorText = err.response.data.response;
            } else if (err.message) {
                errorText = `Error: ${err.message}`;
            }
            
            setError(errorText);
            const errorMessage = {
                text: errorText,
                sender: 'bot',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(e);
        }
    };

    const TypeWriter = ({ text, shouldAnimate }) => {
        const [displayText, setDisplayText] = useState(shouldAnimate ? '' : text);
        
        useEffect(() => {
            if (!shouldAnimate) {
                setDisplayText(text);
                return;
            }

            let index = 0;
            const timer = setInterval(() => {
                if (index < text.length) {
                    setDisplayText((prev) => prev + text.charAt(index));
                    index++;
                } else {
                    clearInterval(timer);
                    setDisplayText(text);
                }
            }, 15);

            return () => clearInterval(timer);
        }, [text, shouldAnimate]);

        return <p className={shouldAnimate ? 'typing' : 'static'}>{displayText}</p>;
    };

    const ProductCard = ({ product }) => {
        const fallbackImage = 'https://via.placeholder.com/400x400/667eea/ffffff?text=' + encodeURIComponent(product.name.substring(0, 20));
        
        // Try multiple image sources
        const imageSources = [
            product.image,
            `https://source.unsplash.com/400x400/?${encodeURIComponent(product.name.split(' ')[0] || 'product')}`,
            fallbackImage
        ].filter(Boolean);
        
        const [imageSrc, setImageSrc] = useState(imageSources[0] || fallbackImage);
        const [imageError, setImageError] = useState(false);
        
        // Update image source when product changes
        useEffect(() => {
            setImageSrc(imageSources[0] || fallbackImage);
            setImageError(false);
        }, [product.image, product.name]);
        
        const handleLinkClick = (url, platform) => {
            window.open(url, '_blank', 'noopener,noreferrer');
        };
        
        const handleImageError = () => {
            const currentIndex = imageSources.indexOf(imageSrc);
            if (currentIndex < imageSources.length - 1) {
                // Try next image source
                setImageSrc(imageSources[currentIndex + 1]);
            } else {
                // All sources failed
                setImageError(true);
                setImageSrc(fallbackImage);
            }
        };
        
        return (
            <div className="product-card">
                <div className="product-image-container">
                    <img 
                        src={imageSrc || fallbackImage} 
                        alt={product.name}
                        className="product-image"
                        onError={handleImageError}
                        onLoad={() => setImageError(false)}
                        loading="lazy"
                    />
                    {product.inStock !== false && <span className="stock-badge">In Stock</span>}
                </div>
                <div className="product-info">
                    <h3 className="product-name">{product.name}</h3>
                    <p className="product-description">{product.description}</p>
                    <div className="product-footer">
                        <div className="product-rating">
                            <span className="stars">{'★'.repeat(Math.floor(parseFloat(product.rating) || 4))}</span>
                            <span className="rating-value">{product.rating || '4.0'}</span>
                        </div>
                        <div className="product-price">{product.price || 'Check website'}</div>
                    </div>
                    <div className="purchase-links">
                        {product.flipkart_link && (
                            <button 
                                className="purchase-btn flipkart-btn"
                                onClick={() => handleLinkClick(product.flipkart_link, 'Flipkart')}
                            >
                                🛒 Buy on Flipkart
                            </button>
                        )}
                        {product.amazon_link && (
                            <button 
                                className="purchase-btn amazon-btn"
                                onClick={() => handleLinkClick(product.amazon_link, 'Amazon')}
                            >
                                🛒 Buy on Amazon
                            </button>
                        )}
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="chatbot-container">
            <div className="chat-header">
                <div className="header-content">
                    <div className="bot-info">
                        <div className="bot-avatar">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M19 3H5C3.89543 3 3 3.89543 3 5V15C3 16.1046 3.89543 17 5 17H8L12 21L16 17H19C20.1046 17 21 16.1046 21 15V5C21 3.89543 20.1046 3 19 3Z" fill="#4a90e2"/>
                                <circle cx="8" cy="10" r="1.5" fill="white"/>
                                <circle cx="12" cy="10" r="1.5" fill="white"/>
                                <circle cx="16" cy="10" r="1.5" fill="white"/>
                            </svg>
                        </div>
                        <div className="bot-status">
                            <h2>🛍️ E-Commerce Support</h2>
                            <span className="status-indicator">Online</span>
                        </div>
                    </div>
                </div>
            </div>
            <div className="chat-messages">
                {messages.map((message, index) => (
                    <div key={index} className={`message ${message.sender}`}>
                        <div className="message-content">
                            {message.sender === 'bot' ? (
                                <>
                                    <TypeWriter 
                                        text={message.text} 
                                        shouldAnimate={index === messages.length - 1 && message.sender === 'bot' && !inputMessage.length} 
                                    />
                                    {message.products && message.products.length > 0 && (
                                        <div className="products-container">
                                            <h4 className="products-title">📦 Recommended Products:</h4>
                                            <div className="products-grid">
                                                {message.products.map((product, idx) => (
                                                    <ProductCard key={product.id || product.name || idx} product={product} />
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <p>{message.text}</p>
                            )}
                            <small>{new Date(message.timestamp).toLocaleTimeString()}</small>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message bot">
                        <div className="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <form onSubmit={sendMessage} className="input-form">
                <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask about products, orders, or get help..."
                    rows="1"
                    className={`chat-input ${inputMessage.length > 0 ? 'typing' : ''}`}
                />
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Sending...' : 'Send'}
                </button>
            </form>
            {error && <div className="error-message">{error}</div>}
        </div>
    );
};

export default ChatBot;