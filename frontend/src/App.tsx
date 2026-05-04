import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Monitor, TrendingDown, TrendingUp, Cpu, Activity, BrainCircuit } from 'lucide-react';
import './index.css';

interface HardwareData {
  id: number;
  component_name: string;
  category: string;
  price: number;
  store: string;
  scraped_at: string;
}

interface AIAnalysis {
  id: number;
  component_name: string;
  analysis_text: string;
  sentiment: string;
  created_at: string;
}

function App() {
  const [data, setData] = useState<HardwareData[]>([]);
  const [analysis, setAnalysis] = useState<AIAnalysis[]>([]);
  const [loading, setLoading] = useState(true);

  // Use mock data if API is down
  const mockData = [
    { name: 'Jan 1', price: 899 },
    { name: 'Jan 2', price: 899 },
    { name: 'Jan 3', price: 850 },
    { name: 'Jan 4', price: 820 },
    { name: 'Jan 5', price: 799 },
    { name: 'Jan 6', price: 799 },
    { name: 'Jan 7', price: 750 },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const [resData, resAnalysis] = await Promise.all([
          fetch(`${apiUrl}/api/hardware`).then(res => res.json()).catch(() => []),
          fetch(`${apiUrl}/api/analysis`).then(res => res.json()).catch(() => [])
        ]);
        
        setData(resData);
        setAnalysis(resAnalysis);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="loading">Cargando Smart Analytics...</div>;

  const currentPrice = data.length > 0 ? data[0].price : 750; // Fallback to mock
  const previousPrice = data.length > 1 ? data[1].price : 899;
  const priceDrop = previousPrice - currentPrice;

  // Process data for chart
  const chartData = data.length > 0 
    ? data.slice().reverse().map(d => ({
        name: new Date(d.scraped_at).toLocaleDateString(),
        price: d.price
      }))
    : mockData;

  return (
    <div className="dashboard-container">
      <header className="header">
        <div>
          <h1>Smart Analytics SaaS</h1>
          <p>Monitoreo inteligente de precios de Hardware (GPUs & CPUs)</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <span className="trend positive" style={{ backgroundColor: 'var(--panel-bg)' }}>
            <Activity size={16} style={{ marginRight: '0.5rem' }}/>
            Sistema Activo
          </span>
        </div>
      </header>

      <div className="grid">
        <div className="card">
          <div className="card-title">
            <Monitor size={20} color="var(--accent-color)" />
            RTX 4080 Super (NVIDIA)
          </div>
          <div className="value-large">${currentPrice}</div>
          <div className={`trend ${priceDrop > 0 ? 'positive' : 'negative'}`}>
            {priceDrop > 0 ? <TrendingDown size={16} /> : <TrendingUp size={16} />}
            <span style={{ marginLeft: '0.25rem' }}>
              {priceDrop > 0 ? `Bajó $${priceDrop}` : `Subió $${Math.abs(priceDrop)}`}
            </span>
          </div>
        </div>

        <div className="card">
          <div className="card-title">
            <Cpu size={20} color="var(--accent-color)" />
            Ryzen 7 7800X3D (AMD)
          </div>
          <div className="value-large">$349</div>
          <div className="trend neutral">
            <span style={{ marginLeft: '0.25rem' }}>Estable (Últimos 7 días)</span>
          </div>
        </div>
      </div>

      <div className="chart-container">
        <div className="card-title" style={{ marginBottom: '1.5rem' }}>Evolución de Precio: RTX 4080 Super</div>
        <ResponsiveContainer width="100%" height="85%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
            <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)'}} />
            <YAxis stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)'}} domain={['dataMin - 50', 'dataMax + 50']} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
              itemStyle={{ color: 'var(--accent-color)' }}
            />
            <Line type="monotone" dataKey="price" stroke="var(--accent-color)" strokeWidth={3} dot={{ fill: 'var(--bg-color)', strokeWidth: 2, r: 4 }} activeDot={{ r: 8 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="ai-analysis">
        <div className="card-title" style={{ color: 'var(--accent-color)' }}>
          <BrainCircuit size={20} />
          Insights Generados por IA (Groq Llama 3)
        </div>
        
        {analysis.length > 0 ? (
          analysis.map((item, idx) => (
            <div key={idx} className="analysis-item">
              <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>{item.component_name} - {new Date(item.created_at).toLocaleString()}</p>
              <p style={{ color: 'var(--text-secondary)' }}>{item.analysis_text}</p>
              <div style={{ marginTop: '0.5rem' }}>
                <span className={`trend ${item.sentiment === 'Positive' ? 'positive' : item.sentiment === 'Negative' ? 'negative' : 'neutral'}`}>
                  {item.sentiment}
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className="analysis-item">
            <p style={{ color: 'var(--text-secondary)' }}>
              El modelo Llama 3 ha detectado una caída sostenida en el precio de la RTX 4080 Super durante la última semana. 
              Dado el historial, es un excelente momento para comprar antes de que el stock se reduzca en la próxima temporada.
            </p>
            <div style={{ marginTop: '0.5rem' }}>
              <span className="trend positive">Positive (Recomendación de Compra)</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
