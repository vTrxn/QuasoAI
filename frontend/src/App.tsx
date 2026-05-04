import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Monitor, TrendingDown, TrendingUp, Cpu, Activity, BrainCircuit } from 'lucide-react';
import './index.css';
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
  recommendation?: string;
  is_alert?: boolean;
  created_at: string;
}

function App() {
  const [data, setData] = useState<HardwareData[]>([]);
  const [analysis, setAnalysis] = useState<AIAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const [resData, resAnalysis] = await Promise.all([
        fetch(`${apiUrl}/api/hardware`).then(res => res.json()).catch(() => []),
        fetch(`${apiUrl}/api/analysis`).then(res => res.json()).catch(() => [])
      ]);
      
      setData(Array.isArray(resData) ? resData : []);
      setAnalysis(Array.isArray(resAnalysis) ? resAnalysis : []);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Cargando Quaso Platform...</div>;

  const currentPrice = data.length > 0 ? data[0].price : 0;
  const previousPrice = data.length > 1 ? data[1].price : currentPrice;
  const priceDrop = previousPrice - currentPrice;

  const filteredData = selectedCategory === 'All' 
    ? data 
    : data.filter(d => d.category === selectedCategory);

  const chartData = filteredData.length > 0 
    ? filteredData.slice().reverse().map(d => ({
        name: new Date(d.scraped_at).toLocaleDateString(),
        price: d.price
      }))
    : [];

  const barChartData = data.reduce((acc: any[], curr) => {
    if (!acc.find(i => i.name === curr.component_name)) {
      acc.push({ name: curr.component_name, price: curr.price });
    }
    return acc;
  }, []).slice(0, 5); // top 5 unique components

  return (
    <div className="dashboard-container">
      <header className="header">
        <div>
          <h1>Quaso: Inteligencia de Datos</h1>
          <p>Bienvenido</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span className="trend positive" style={{ backgroundColor: 'var(--panel-bg)' }}>
            <Activity size={16} style={{ marginRight: '0.5rem' }}/>
            Motor Activo
          </span>
        </div>
      </header>

      <div className="grid">
        <div className="card">
          <div className="card-title">
            <Monitor size={20} color="var(--accent-color)" />
            Monitor de Precios
          </div>
          <div className="value-large">{currentPrice > 0 ? `$${currentPrice}` : 'Sin datos'}</div>
          {currentPrice > 0 && (
            <div className={`trend ${priceDrop > 0 ? 'positive' : priceDrop < 0 ? 'negative' : 'neutral'}`}>
              {priceDrop > 0 ? <TrendingDown size={16} /> : priceDrop < 0 ? <TrendingUp size={16} /> : null}
              <span style={{ marginLeft: '0.25rem' }}>
                {priceDrop > 0 ? `Bajó $${priceDrop}` : priceDrop < 0 ? `Subió $${Math.abs(priceDrop)}` : 'Estable'}
              </span>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-title">
            <Cpu size={20} color="var(--accent-color)" />
            Categoría: Hardware
          </div>
          <div className="value-large">{data.length}</div>
          <div className="trend neutral">
            <span style={{ marginLeft: '0.25rem' }}>Registros totales</span>
          </div>
        </div>

        <div className="card">
          <div className="card-title">
            <Monitor size={20} color="var(--accent-color)" />
            Filtro por Categoría
          </div>
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '8px', backgroundColor: 'var(--bg-color)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', marginTop: '0.5rem' }}
          >
            <option value="All">Todas las Categorías</option>
            <option value="GPU">Tarjetas Gráficas (GPU)</option>
            <option value="CPU">Procesadores (CPU)</option>
          </select>
        </div>
      </div>

      {chartData.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="chart-container" style={{ marginBottom: 0 }}>
            <div className="card-title" style={{ marginBottom: '1.5rem' }}>Evolución Temporal de Precios</div>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)'}} />
                <YAxis stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)'}} domain={['auto', 'auto']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
                  itemStyle={{ color: 'var(--accent-color)' }}
                />
                <Line type="monotone" dataKey="price" stroke="var(--accent-color)" strokeWidth={3} dot={{ fill: 'var(--bg-color)', strokeWidth: 2, r: 4 }} activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="chart-container" style={{ marginBottom: 0 }}>
            <div className="card-title" style={{ marginBottom: '1.5rem' }}>Comparativa Actual (Top 5)</div>
            <ResponsiveContainer width="100%" height="85%">
              <BarChart data={barChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)'}} />
                <YAxis stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)'}} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
                  itemStyle={{ color: 'var(--accent-color)' }}
                />
                <Bar dataKey="price" fill="var(--accent-color)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="ai-analysis">
        <div className="card-title" style={{ color: 'var(--accent-color)' }}>
          <BrainCircuit size={20} />
          AI Insights (Motor de Decisiones)
        </div>
        
        {analysis.length > 0 ? (
          analysis.map((item, idx) => (
            <div key={idx} className="analysis-item">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <p style={{ fontWeight: 600, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {item.component_name} 
                  {item.is_alert && <span style={{ backgroundColor: 'var(--danger)', color: 'white', padding: '0.1rem 0.4rem', borderRadius: '4px', fontSize: '0.75rem' }}>Alerta de Precio</span>}
                </p>
                <span className={`trend ${item.sentiment === 'Positivo' ? 'positive' : item.sentiment === 'Negativo' ? 'negative' : 'neutral'}`}>
                  {item.sentiment}
                </span>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{item.analysis_text}</p>
              {item.recommendation && (
                <div style={{ marginTop: '0.75rem', fontWeight: 700 }}>
                  Recomendación: <span style={{ color: 'var(--accent-color)' }}>{item.recommendation}</span>
                </div>
              )}
              <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                {new Date(item.created_at).toLocaleString()}
              </p>
            </div>
          ))
        ) : (
          <div className="analysis-item">
            <p style={{ color: 'var(--text-secondary)' }}>No hay análisis disponibles. Inicia el motor de datos para generar insights.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
