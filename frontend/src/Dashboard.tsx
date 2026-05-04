import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { 
  Activity, AlertTriangle, Cpu, DollarSign, TrendingDown, TrendingUp, Search 
} from 'lucide-react';

interface TrafficLight {
  status: 'Green' | 'Red' | 'Yellow';
  recommendation: string;
  color: string;
}

interface GlitchData {
  is_glitch: boolean;
  drop_percentage?: number;
  avg_price?: number;
}

interface ComponentDashboardData {
  id: number;
  name: string;
  category: string;
  current_price: number;
  traffic_light: TrafficLight;
  glitch_hunter: GlitchData;
  history: { price: number }[];
}

const Dashboard: React.FC = () => {
  const [components, setComponents] = useState<ComponentDashboardData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/components/dashboard');
      if (res.ok) {
        const data = await res.json();
        setComponents(data);
      }
    } catch (error) {
      console.error("Error fetching data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Green': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'Red': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
      case 'Yellow': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      default: return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  const filteredComponents = components.filter(c => 
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    c.id.toString() === searchQuery
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-6 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center pb-4 border-b border-slate-800 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-2">
              <Cpu className="text-indigo-500" />
              Quaso<span className="text-indigo-500 font-light">AI</span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">Enterprise Hardware Intelligence Platform</p>
          </div>
          
          <div className="flex gap-4 items-center">
            <button onClick={fetchData} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm transition-colors cursor-pointer">
              Actualizar
            </button>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
              <input 
                type="text" 
                placeholder="Buscar Componente..."
                className="bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all w-64"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </header>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-pulse flex flex-col items-center gap-3">
              <Activity className="text-indigo-500 w-8 h-8 animate-spin-slow" />
              <span className="text-slate-500 text-sm">Cargando mercado en tiempo real...</span>
            </div>
          </div>
        ) : filteredComponents.length === 0 ? (
          <div className="text-center py-20 text-slate-500 bg-slate-900 border border-slate-800 rounded-xl">
            <p>No se encontraron componentes.</p>
            <p className="text-sm mt-2">Usa el comando /search o ingesta enlaces en el bot de Telegram para llenar la base de datos.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {filteredComponents.map((intel) => {
              const avgPrice = intel.history.length > 0 ? intel.history.reduce((acc, curr) => acc + curr.price, 0) / intel.history.length : intel.current_price;
              
              return (
                <div key={intel.id} className="bg-slate-900 rounded-xl border border-slate-800 p-6 flex flex-col xl:flex-row gap-6 shadow-xl shadow-black/20 hover:border-slate-700 transition-colors">
                  {/* Left Column: Info & Stats */}
                  <div className="flex-1 space-y-4">
                    <div>
                      <div className="text-xs text-indigo-400 font-bold tracking-wider uppercase mb-1">#{intel.id} • {intel.category}</div>
                      <h2 className="text-2xl font-bold text-white">{intel.name}</h2>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Price Card */}
                      <div className="bg-slate-950/50 rounded-lg p-4 border border-slate-800">
                        <div className="text-sm text-slate-400 mb-1 flex justify-between">
                          <span>Precio Actual</span>
                          <DollarSign className="w-4 h-4 text-slate-500" />
                        </div>
                        <div className="text-2xl font-bold text-white mb-1">
                          ${intel.current_price.toLocaleString('es-CO')}
                        </div>
                      </div>

                      {/* Traffic Light Card */}
                      <div className={`rounded-lg p-4 border ${getStatusColor(intel.traffic_light.status)}`}>
                        <div className="text-sm opacity-80 mb-1 flex justify-between">
                          <span>Decisión IA</span>
                          {intel.traffic_light.status === 'Green' ? <TrendingDown className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
                        </div>
                        <div className="font-bold mb-1">{intel.traffic_light.status === 'Green' ? 'COMPRAR' : intel.traffic_light.status === 'Red' ? 'ESPERAR' : 'PROMEDIO'}</div>
                        <p className="text-xs opacity-90 truncate" title={intel.traffic_light.recommendation}>{intel.traffic_light.recommendation}</p>
                      </div>
                    </div>

                    {intel.glitch_hunter.is_glitch && (
                      <div className="bg-amber-500/10 border border-amber-500/30 text-amber-500 rounded-lg p-3 flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                        <div>
                          <div className="font-bold text-sm">GLITCH DETECTADO</div>
                          <div className="text-xs text-amber-400/80">Caída del {intel.glitch_hunter.drop_percentage}% vs media.</div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Right Column: Chart */}
                  <div className="flex-1 xl:max-w-xl h-48 xl:h-auto border border-slate-800/50 bg-slate-950/30 rounded-lg p-4 relative">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={intel.history} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <YAxis 
                          domain={['auto', 'auto']}
                          stroke="#64748b" 
                          fontSize={10}
                          tickLine={false}
                          axisLine={false}
                          tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                          width={50}
                        />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '0.5rem', fontSize: '12px' }}
                          itemStyle={{ color: '#818cf8' }}
                          formatter={(value: any) => [`$${Number(value).toLocaleString('es-CO')}`, 'Precio']}
                          labelFormatter={() => ''}
                        />
                        <ReferenceLine y={avgPrice} stroke="#475569" strokeDasharray="3 3" />
                        <Line 
                          type="monotone" 
                          dataKey="price" 
                          stroke={intel.traffic_light.status === 'Green' ? '#34d399' : intel.traffic_light.status === 'Red' ? '#fb7185' : '#6366f1'}
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 4, strokeWidth: 0 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;