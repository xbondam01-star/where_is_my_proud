import React from 'react';
import { MapPin, Zap } from 'lucide-react';
import './BeerCard.css';

const BeerCard = ({ deal }) => {
    // If we don't pass a deal, use dummy data mimicking the design
    const displayDeal = deal || {
        store: 'Albert (300m)',
        price: 28.90,
        volume: '0.5l',
        discount: '-35%' // Added for mockup styling
    };

    return (
        <div className="beer-card">
            {/* Background Ghost Icon Overlay */}
            <div className="ghost-icon">
                <svg width="120" height="150" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17 11h1a3 3 0 0 1 0 6h-1"></path>
                    <path d="M9 7l1-4h4l1 4"></path>
                    <path d="M7 21h10a2 2 0 0 0 2-2V7H5v12a2 2 0 0 0 2 2z"></path>
                </svg>
            </div>

            <div className="card-header">
                <span className="offer-type">LIMITED OFFER</span>
                <div className="badge">
                    <Zap size={14} className="badge-icon" />
                    <span>BEST DEAL</span>
                </div>
            </div>

            <h2 className="product-title">Proud ležák</h2>

            <div className="price-container">
                <span className="price-main">{displayDeal.price.toFixed(2)}</span>
                <span className="price-sub">Kč / {displayDeal.volume}</span>
            </div>

            <div className="card-footer">
                <div className="location-pill">
                    <MapPin size={16} />
                    <span>{displayDeal.store}</span>
                </div>
                <span className="discount-perc">{displayDeal.discount}</span>
            </div>
        </div>
    );
};

export default BeerCard;
