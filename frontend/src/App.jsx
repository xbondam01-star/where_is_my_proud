import { useState, useEffect } from 'react'
import { User } from 'lucide-react'
import './index.css'
import BeerCard from './components/BeerCard'
import Radar from './components/Radar'
import { fetchBestDeal } from './api/client'

function App() {
    const [bestDeal, setBestDeal] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const loadDeal = async () => {
            const deal = await fetchBestDeal()
            if (deal) {
                setBestDeal({
                    store: deal.store,
                    price: deal.price_per_unit,
                    volume: deal.volume_liters + 'l',
                    discount: '-10%' // Mocked for design
                })
            }
            setLoading(false)
        }
        loadDeal()
    }, [])

    return (
        <>
            <header className="header">
                <div className="logo-container">
                    <h1 className="logo">
                        Where is my <span className="highlight-text">Proud</span>
                    </h1>
                    <p className="subtitle">PRICE TRACKER & NAVIGATOR</p>
                </div>
                <button className="profile-button">
                    <User size={24} color="var(--color-primary)" />
                </button>
            </header>

            <main className="main-content">
                {loading ? (
                    <div style={{ color: 'var(--text-secondary)' }}>Loading best deal...</div>
                ) : (
                    <>
                        <BeerCard deal={bestDeal} />
                        <Radar storeName={bestDeal?.store || "Lidl Market"} />
                    </>
                )}
            </main>
        </>
    )
}

export default App
