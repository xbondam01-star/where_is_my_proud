// Dynamically point to the backend using the same IP address running the frontend
const hostname = window.location.hostname;
const BASE_URL = `http://${hostname}:8000`;

export const fetchBestDeal = async () => {
    try {
        const response = await fetch(`${BASE_URL}/deals/best`);
        if (!response.ok) {
            if (response.status === 404) return null;
            throw new Error(`Error fetching best deal: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("API Fetch Error (Best Deal):", error);
        return null; // Gracefully fail
    }
};

export const fetchAllDeals = async () => {
    try {
        const response = await fetch(`${BASE_URL}/deals`);
        if (!response.ok) {
            throw new Error(`Error fetching deals: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("API Fetch Error (All Deals):", error);
        return [];
    }
};
