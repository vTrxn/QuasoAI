import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Monitor, TrendingDown, TrendingUp, Cpu, Activity, BrainCircuit, LogOut } from 'lucide-react';
import { supabase } from './supabaseClient';
import Login from './Login';
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
  created_at: string;
}

function App() {
  const [session, setSession] = useState<any>(null);
  const [data, setData] = useState<HardwareData[]>([]);
  const [analysis, setAnalysis] = useState<AIAnalysis[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) fetchData(session.access_token);
      else setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) fetchData(session.access_token);
      else setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const fetchData = async (token: string) => {
    setLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const headers = {
        'Authorization': `Bearer ${token}`
      };
      
      const [resData, resAnalysis] = await Promise.all([
        fetch(`${apiUrl}/api/hardware`, { headers }).then(res => res.json()).catch(() => []),
        fetch(`${apiUrl}/api/analysis`, { headers }).then(res => res.json()).catch(() => [])
      ]);
      
      setData(Array.isArray(resData) ? resData : []);
      setAnalysis(Array.isArray(resAnalysis) ? resAnalysis : []);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setSession(null);
  };

  if (loading) return <div className="loading">Cargando Quaso Platform...</div>;
  if (!session) return <Login onLogin={() => {}} />;

  const currentPrice = data.length > 0 ? data[0].price : 0;
  const previousPrice = data.length > 1 ? data[1].price : currentPrice;
  const priceDrop = previousPrice - currentPrice;

  const chartData = data.length > 0 
    ? data.slice().reverse().map(d => ({
        name: new Date(d.scraped_at).toLocaleDateString(),
        price: d.price
      }))
    : [];

  return (
    <div className="dashboard-container">
      <header className="header">
        <div>
          <h1>Quaso: Inteligencia de Datos</h1>
          <p>Bienvenido, {session.user.email}</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span className="trend positive" style={{ backgroundColor: 'var(--panel-bg)' }}>
            <Activity size={16} style={{ marginRight: '0.5rem' }}/>
            Motor Activo
          </span>
          <button onClick={handleLogout} className="btn btn-secondary" style={{ width: 'auto', padding: '0.5rem 1rem', marginTop: 0 }}>
            <LogOut size={16} />
          </button>
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
      </div>

      {chartData.length > 0 && (
        <div className="chart-container">
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
                <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>{item.component_name}</p>
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
