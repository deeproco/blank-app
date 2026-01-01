import React, { useState, useEffect, useMemo } from 'react';
import { 
  Map, 
  Calendar, 
  Clock, 
  MapPin, 
  Plus, 
  Trash2,
  MoveUp,
  MoveDown,
  Navigation,
  Car,
  Utensils,
  Camera,
  Hotel,
  Coffee,
  Save,
  Share2,
  Edit2,
  Ticket,
  FileText,
  Link as LinkIcon,
  X,
  Sparkles,
  Loader2,
  Banknote
} from 'lucide-react';

// --- Gemini API Helpers ---

const generateGeminiContent = async (prompt, schema = null) => {
  const apiKey = ""; // Runtime injection
  try {
    const payload = {
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        responseMimeType: schema ? "application/json" : "text/plain",
      }
    };

    if (schema) {
      payload.generationConfig.responseSchema = schema;
    }

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }
    );

    const data = await response.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
    
    if (schema && text) {
      return JSON.parse(text);
    }
    return text;
  } catch (error) {
    console.error("Gemini API Error:", error);
    return null;
  }
};

// --- Mock Data & Types ---

const INITIAL_TRIP = {
  id: 'trip-1',
  title: 'Weekend in Tokyo',
  startDate: '2024-04-10',
  days: [
    {
      id: 'day-1',
      date: '2024-04-10',
      label: 'Day 1',
      stops: [
        { 
          id: 's1', 
          type: 'transport', 
          name: 'Arrive at Narita Airport', 
          startTime: '10:00', 
          duration: 60, 
          category: 'transport',
          ticketInfo: 'Flight JL123',
          remarks: 'Pick up pocket WiFi at terminal',
          expenses: '¥2,000'
        },
        { 
          id: 's2', 
          type: 'visit', 
          name: 'Check-in Hotel Shinjuku', 
          startTime: '12:00', 
          duration: 45, 
          category: 'hotel',
          googleLink: 'https://maps.google.com/?q=Shinjuku+Hotel',
          expenses: '¥15,000'
        },
        { id: 's3', type: 'food', name: 'Ramen Lunch', startTime: '13:00', duration: 60, category: 'food', expenses: '¥1,200' },
        { id: 's4', type: 'sight', name: 'Meiji Jingu Shrine', startTime: '14:30', duration: 90, category: 'sight', expenses: 'Free' },
        { id: 's5', type: 'sight', name: 'Shibuya Crossing', startTime: '16:30', duration: 60, category: 'sight' },
      ]
    },
    {
      id: 'day-2',
      date: '2024-04-11',
      label: 'Day 2',
      stops: [
        { id: 's6', type: 'food', name: 'Breakfast at Tsukiji', startTime: '08:00', duration: 90, category: 'food', expenses: '¥3,500' },
        { id: 's7', type: 'sight', name: 'TeamLab Planets', startTime: '10:00', duration: 120, category: 'sight', ticketInfo: 'QR Code saved in gallery', expenses: '¥3,200' },
      ]
    }
  ]
};

const CATEGORY_ICONS = {
  transport: Navigation,
  hotel: Hotel,
  food: Utensils,
  sight: Camera,
  coffee: Coffee,
  default: MapPin
};

const CATEGORY_COLORS = {
  transport: 'bg-blue-100 text-blue-600',
  hotel: 'bg-purple-100 text-purple-600',
  food: 'bg-orange-100 text-orange-600',
  sight: 'bg-green-100 text-green-600',
  coffee: 'bg-amber-100 text-amber-600',
  default: 'bg-gray-100 text-gray-600'
};

// --- Helper Functions ---

const addMinutes = (timeStr, mins) => {
  const [h, m] = timeStr.split(':').map(Number);
  const totalMins = h * 60 + m + mins;
  const newH = Math.floor(totalMins / 60) % 24;
  const newM = totalMins % 60;
  return `${String(newH).padStart(2, '0')}:${String(newM).padStart(2, '0')}`;
};

const calculateSchedule = (stops) => {
  if (stops.length === 0) return [];
  
  let currentStartTime = stops[0].startTime; 
  
  return stops.map((stop, index) => {
    if (index > 0) {
      const prevStop = stops[index - 1];
      const travelTime = 30; 
      currentStartTime = addMinutes(prevStop.startTime, prevStop.duration + travelTime);
    }
    return { ...stop, startTime: currentStartTime };
  });
};

// --- Components ---

const Header = ({ title, days, activeDayId, onEditDay }) => {
  const activeDay = days.find(d => d.id === activeDayId);
  return (
    <div className="bg-white shadow-sm z-20 relative">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center text-white shadow-emerald-200 shadow-lg">
            <Map size={20} />
          </div>
          <div>
            <h1 className="font-bold text-gray-800 text-lg leading-tight">{title}</h1>
            <button 
              onClick={() => onEditDay(activeDay)}
              className="group flex items-center gap-2 text-xs text-gray-500 hover:text-emerald-600 transition-colors text-left"
            >
              <span>{activeDay?.label} • {activeDay?.date}</span>
              <Edit2 size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />
            </button>
          </div>
        </div>
        <div className="flex gap-2">
           <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-full transition-colors">
            <Share2 size={20} />
          </button>
          <button className="p-2 text-emerald-600 bg-emerald-50 hover:bg-emerald-100 rounded-full transition-colors">
            <Save size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

const DayTabs = ({ days, activeDayId, setActiveDayId, onAddDay, onEditDay, onOpenAI }) => {
  return (
    <div className="flex overflow-x-auto bg-white border-b border-gray-100 px-4 pt-2 no-scrollbar">
      {days.map((day) => (
        <button
          key={day.id}
          onClick={() => setActiveDayId(day.id)}
          onDoubleClick={() => onEditDay(day)}
          className={`relative group flex-shrink-0 px-4 py-3 mr-4 border-b-2 text-sm font-medium transition-colors ${
            activeDayId === day.id
              ? 'border-emerald-500 text-emerald-600'
              : 'border-transparent text-gray-400 hover:text-gray-600'
          }`}
        >
          {day.label}
          <span className="block text-[10px] font-normal opacity-70 mt-0.5">{day.date}</span>
          
          {/* Edit Icon on active tab */}
          {activeDayId === day.id && (
            <div 
              role="button"
              onClick={(e) => {
                e.stopPropagation();
                onEditDay(day);
              }}
              className="absolute top-2 right-1 p-1.5 text-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 rounded-full hover:bg-emerald-50 shadow-sm"
              title="Edit Day Details"
            >
              <Edit2 size={10} />
            </div>
          )}
        </button>
      ))}
      <button 
        onClick={onAddDay}
        className="flex-shrink-0 px-4 py-3 text-gray-300 hover:text-emerald-500 transition-colors"
        title="Add Day"
      >
        <Plus size={20} />
      </button>
      
      {/* Magic AI Button */}
      <button
        onClick={onOpenAI}
        className="ml-auto flex-shrink-0 flex items-center gap-1.5 px-3 py-1 my-2 text-xs font-bold text-violet-600 bg-violet-50 hover:bg-violet-100 rounded-lg transition-colors border border-violet-100"
      >
        <Sparkles size={14} />
        Magic Plan
      </button>
    </div>
  );
};

const StopCard = ({ stop, index, isLast, onMoveUp, onMoveDown, onDelete, onChangeDuration, onEdit, onEnrich }) => {
  const Icon = CATEGORY_ICONS[stop.category] || CATEGORY_ICONS.default;
  const colorClass = CATEGORY_COLORS[stop.category] || CATEGORY_COLORS.default;
  const endTime = addMinutes(stop.startTime, stop.duration);
  const [isEnriching, setIsEnriching] = useState(false);

  const handleEnrich = async (e) => {
    e.stopPropagation();
    setIsEnriching(true);
    await onEnrich(stop);
    setIsEnriching(false);
  };

  return (
    <div className="relative flex group">
      {/* Timeline Line */}
      <div className="flex flex-col items-center mr-4 min-w-[50px]">
        <div className="text-xs font-semibold text-gray-600 mb-1">{stop.startTime}</div>
        <div className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center ${colorClass} shadow-sm border-2 border-white`}>
          <Icon size={14} />
        </div>
        {!isLast && (
          <div className="w-0.5 h-full bg-gray-200 my-1 relative">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gray-50 text-[10px] text-gray-400 border border-gray-100 px-1.5 py-0.5 rounded-full flex items-center gap-1 whitespace-nowrap">
              <Car size={8} /> 30m
            </div>
          </div>
        )}
      </div>

      {/* Card Content */}
      <div className="flex-1 pb-6">
        <div 
          onClick={() => onEdit(stop)}
          className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow group-hover:border-emerald-100 cursor-pointer"
        >
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-bold text-gray-800">{stop.name}</h3>
            <div 
              onClick={(e) => e.stopPropagation()}
              className="flex gap-1"
            >
              <button 
                onClick={handleEnrich} 
                className={`p-1 rounded text-violet-400 hover:text-violet-600 hover:bg-violet-50 transition-all ${isEnriching ? 'animate-pulse' : ''}`} 
                title="Get AI Insider Tip"
                disabled={isEnriching}
              >
                {isEnriching ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
              </button>
              <button onClick={() => onEdit(stop)} className="p-1 hover:bg-emerald-50 rounded text-gray-400 hover:text-emerald-600" title="Edit Details">
                <Edit2 size={14} />
              </button>
              <button onClick={() => onMoveUp(index)} disabled={index === 0} className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600 disabled:opacity-30">
                <MoveUp size={14} />
              </button>
              <button onClick={() => onMoveDown(index)} disabled={isLast} className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600 disabled:opacity-30">
                <MoveDown size={14} />
              </button>
              <button onClick={() => onDelete(stop.id)} className="p-1 hover:bg-red-50 rounded text-gray-400 hover:text-red-500">
                <Trash2 size={14} />
              </button>
            </div>
          </div>
          
          <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
            <div 
              onClick={(e) => e.stopPropagation()}
              className="flex items-center gap-1 bg-gray-50 px-2 py-1 rounded-md"
            >
              <Clock size={12} />
              <span>{stop.duration} min</span>
              <div className="flex gap-1 ml-2 border-l pl-2 border-gray-200">
                <button onClick={() => onChangeDuration(stop.id, -15)} className="hover:text-emerald-600">-</button>
                <button onClick={() => onChangeDuration(stop.id, 15)} className="hover:text-emerald-600">+</button>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-gray-300">|</span>
              <span>Until {endTime}</span>
            </div>
          </div>

          {/* Additional Fields Display */}
          {(stop.ticketInfo || stop.googleLink || stop.expenses || stop.remarks) && (
            <div className="space-y-1.5 pt-2 border-t border-gray-50">
               {stop.expenses && (
                <div className="flex items-center gap-2 text-xs text-emerald-600 bg-emerald-50/50 p-1.5 rounded border border-emerald-100/50">
                  <Banknote size={12} className="flex-shrink-0" />
                  <span className="truncate font-medium">{stop.expenses}</span>
                </div>
              )}
               {stop.ticketInfo && (
                <div className="flex items-center gap-2 text-xs text-slate-600 bg-amber-50/50 p-1.5 rounded border border-amber-100/50">
                  <Ticket size={12} className="text-amber-500 flex-shrink-0" />
                  <span className="truncate font-medium">{stop.ticketInfo}</span>
                </div>
              )}
              {stop.googleLink && (
                 <a href={stop.googleLink} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-xs text-blue-600 hover:underline hover:bg-blue-50 p-1.5 rounded transition-colors">
                   <LinkIcon size={12} className="flex-shrink-0" />
                   <span className="truncate">Open Map Location</span>
                 </a>
              )}
              {stop.remarks && (
                <div className="flex items-start gap-2 text-xs text-slate-500 p-1.5 bg-slate-50/50 rounded">
                   <FileText size={12} className="mt-0.5 flex-shrink-0 text-slate-400" />
                   <div className="italic break-words w-full">
                    {stop.remarks.split('\n').map((line, i) => (
                      <p key={i} className={line.startsWith('✨') ? 'text-violet-600 font-medium not-italic mt-1' : ''}>
                        {line}
                      </p>
                    ))}
                   </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const AddStopButton = ({ onClick }) => (
  <button 
    onClick={onClick}
    className="ml-[66px] mb-8 flex items-center gap-2 text-emerald-600 font-medium hover:text-emerald-700 transition-colors group"
  >
    <div className="w-8 h-8 rounded-full border-2 border-emerald-500 border-dashed flex items-center justify-center group-hover:bg-emerald-50">
      <Plus size={16} />
    </div>
    <span>Add new stop</span>
  </button>
);

const SchematicMap = ({ stops, activeDay }) => {
  return (
    <div className="h-full w-full bg-slate-50 relative overflow-hidden flex flex-col items-center justify-center p-8">
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none" 
           style={{ backgroundImage: 'radial-gradient(#444 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
      </div>
      
      <div className="text-center mb-8 z-10">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-white rounded-full shadow-lg mb-3 text-emerald-500">
          <Map size={24} />
        </div>
        <h3 className="font-bold text-gray-700">Route Overview</h3>
        <p className="text-sm text-gray-400">
          {activeDay ? `${activeDay.label} • ${activeDay.date}` : 'Schematic view of your day'}
        </p>
      </div>

      <div className="relative w-full max-w-md h-[400px] border-2 border-dashed border-gray-200 rounded-3xl p-6 flex flex-col justify-between bg-white/50 backdrop-blur-sm">
        {stops.map((stop, i) => (
          <div key={stop.id} className="flex items-center gap-3 relative z-10">
             <div className={`w-3 h-3 rounded-full ${i === 0 || i === stops.length -1 ? 'bg-emerald-500' : 'bg-gray-300'}`}></div>
             
             {/* Enhanced Label with Time Details */}
             <div className="flex flex-col min-w-0">
               <div className="text-xs font-medium text-gray-600 truncate max-w-[150px]">{stop.name}</div>
               <div className="flex items-center gap-1.5 text-[10px] text-gray-400 mt-0.5">
                 <div className="flex items-center gap-0.5 bg-gray-100 px-1 rounded">
                   <Clock size={8} />
                   <span>{stop.startTime}</span>
                 </div>
                 <span>•</span>
                 <span>{stop.duration}m</span>
               </div>
             </div>

             {i !== stops.length - 1 && (
               <div className="absolute left-[5px] top-[14px] w-[2px] h-[calc(100%+14px)] bg-gray-200 -z-10"></div>
             )}
          </div>
        ))}
        {stops.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-gray-300">
            No stops yet
          </div>
        )}
      </div>
    </div>
  );
};

// --- Modals ---

const AIPlannerModal = ({ isOpen, onClose, onGenerate }) => {
  const [location, setLocation] = useState('Tokyo');
  const [vibe, setVibe] = useState('Classic Sightseeing');
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setIsLoading(true);
    
    // Schema for structured JSON response
    const schema = {
      type: "ARRAY",
      items: {
        type: "OBJECT",
        properties: {
          name: { type: "STRING" },
          category: { type: "STRING", enum: ["sight", "food", "hotel", "transport", "coffee"] },
          duration: { type: "INTEGER" },
          remarks: { type: "STRING" },
          expenses: { type: "STRING", description: "Estimated cost (e.g. $20, ¥1000)" }
        },
        required: ["name", "duration", "category"]
      }
    };

    const prompt = `Create a realistic travel itinerary for 1 day in ${location} with a "${vibe}" theme. Return exactly 4 items.`;
    
    const stops = await generateGeminiContent(prompt, schema);
    
    setIsLoading(false);
    if (stops) {
      onGenerate(stops);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="bg-gradient-to-r from-violet-500 to-fuchsia-500 p-6 text-white text-center">
          <Sparkles className="w-12 h-12 mx-auto mb-2 opacity-90" />
          <h3 className="font-bold text-xl">Magic Plan</h3>
          <p className="text-white/80 text-sm">Let AI design your perfect day</p>
        </div>
        
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Where to?</label>
            <input 
              type="text" 
              value={location}
              onChange={e => setLocation(e.target.value)}
              className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-violet-500"
              placeholder="e.g. Paris, Kyoto, New York"
            />
          </div>
          
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Trip Vibe</label>
            <select 
              value={vibe}
              onChange={e => setVibe(e.target.value)}
              className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-violet-500"
            >
              <option>Classic Sightseeing</option>
              <option>Foodie Adventure</option>
              <option>Hidden Gems & Local Spots</option>
              <option>Relaxed & Chill</option>
              <option>History & Culture</option>
              <option>Shopping Spree</option>
            </select>
          </div>

          <button 
            onClick={handleGenerate}
            disabled={isLoading}
            className="w-full py-3 bg-violet-600 hover:bg-violet-700 disabled:bg-violet-300 text-white font-bold rounded-xl transition-colors shadow-lg shadow-violet-200 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Planning...
              </>
            ) : (
              <>
                <Sparkles size={20} />
                Generate Itinerary
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

const StopModal = ({ isOpen, onClose, onSave, initialData }) => {
  const [formData, setFormData] = useState({
    name: '',
    category: 'sight',
    duration: 60,
    googleLink: '',
    ticketInfo: '',
    remarks: '',
    expenses: ''
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        category: initialData.category || 'sight',
        duration: initialData.duration || 60,
        googleLink: initialData.googleLink || '',
        ticketInfo: initialData.ticketInfo || '',
        remarks: initialData.remarks || '',
        expenses: initialData.expenses || ''
      });
    } else {
      setFormData({ name: '', category: 'sight', duration: 60, googleLink: '', ticketInfo: '', remarks: '', expenses: '' });
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ ...formData, duration: parseInt(formData.duration) });
    onClose();
  };

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  return (
    <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200 max-h-[90vh] flex flex-col">
        <div className="p-4 border-b border-gray-100 flex justify-between items-center flex-shrink-0">
          <h3 className="font-bold text-gray-800">{initialData ? 'Edit Stop' : 'Add New Stop'}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={20}/></button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-4 space-y-4 overflow-y-auto">
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Place Name</label>
            <input 
              autoFocus
              type="text" 
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g. Tokyo Tower"
              className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
              required
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
             <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Category</label>
              <select 
                name="category"
                value={formData.category} 
                onChange={handleChange}
                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500"
              >
                <option value="sight">Sightseeing</option>
                <option value="food">Food/Drink</option>
                <option value="hotel">Hotel</option>
                <option value="transport">Transport</option>
                <option value="coffee">Cafe</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Duration (min)</label>
              <input 
                type="number" 
                name="duration"
                value={formData.duration}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500"
                min="15"
                step="15"
              />
            </div>
          </div>

          <div className="border-t border-gray-100 pt-4 space-y-4">
             <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-1 flex items-center gap-1">
                <Banknote size={12}/> Expenses / Cost
              </label>
              <input 
                type="text" 
                name="expenses"
                value={formData.expenses}
                onChange={handleChange}
                placeholder="e.g. ¥2000, $25, Free"
                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-1 flex items-center gap-1">
                <LinkIcon size={12}/> Google Maps Link
              </label>
              <input 
                type="url" 
                name="googleLink"
                value={formData.googleLink}
                onChange={handleChange}
                placeholder="https://goo.gl/maps/..."
                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-1 flex items-center gap-1">
                <Ticket size={12}/> Ticket Info
              </label>
              <input 
                type="text" 
                name="ticketInfo"
                value={formData.ticketInfo}
                onChange={handleChange}
                placeholder="e.g. Reservation #12345, Flight JL123"
                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-1 flex items-center gap-1">
                <FileText size={12}/> Remarks
              </label>
              <textarea 
                name="remarks"
                value={formData.remarks}
                onChange={handleChange}
                placeholder="e.g. Enter through the south gate..."
                rows="2"
                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 text-sm resize-none"
              />
            </div>
          </div>
        </form>

        <div className="p-4 border-t border-gray-100 bg-gray-50 flex-shrink-0">
          <button 
            onClick={handleSubmit}
            className="w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-xl transition-colors shadow-lg shadow-emerald-200"
          >
            {initialData ? 'Save Changes' : 'Add to Itinerary'}
          </button>
        </div>
      </div>
    </div>
  );
};

const DayEditModal = ({ isOpen, onClose, onSave, initialData }) => {
  const [label, setLabel] = useState('');
  const [date, setDate] = useState('');

  useEffect(() => {
    if (initialData) {
      setLabel(initialData.label);
      setDate(initialData.date);
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-4 animate-in fade-in zoom-in duration-200">
         <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold text-gray-800">Edit Day Details</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={20}/></button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Day Label</label>
            <input 
              type="text" 
              value={label}
              onChange={e => setLabel(e.target.value)}
              className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Date</label>
            <input 
              type="date" 
              value={date}
              onChange={e => setDate(e.target.value)}
              className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500"
            />
          </div>
          <button 
            onClick={() => { onSave(label, date); onClose(); }}
            className="w-full py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-xl transition-colors"
          >
            Update Day
          </button>
        </div>
      </div>
    </div>
  );
}

// --- Main App Component ---

export default function App() {
  const [trip, setTrip] = useState(INITIAL_TRIP);
  const [activeDayId, setActiveDayId] = useState(INITIAL_TRIP.days[0].id);
  const [viewMode, setViewMode] = useState('split');
  
  // Modal States
  const [stopModalOpen, setStopModalOpen] = useState(false);
  const [dayModalOpen, setDayModalOpen] = useState(false);
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [editingStop, setEditingStop] = useState(null); 
  const [editingDay, setEditingDay] = useState(null);

  // Get current day's data
  const activeDay = trip.days.find(d => d.id === activeDayId);
  const stops = activeDay?.stops || [];
  const scheduledStops = useMemo(() => calculateSchedule(stops), [stops]);

  // Handlers
  const handleMoveStop = (index, direction) => {
    const newStops = [...stops];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= newStops.length) return;
    [newStops[index], newStops[targetIndex]] = [newStops[targetIndex], newStops[index]];
    updateStops(newStops);
  };

  const handleDeleteStop = (id) => {
    updateStops(stops.filter(s => s.id !== id));
  };

  const handleChangeDuration = (id, delta) => {
    updateStops(stops.map(s => s.id === id ? { ...s, duration: Math.max(15, s.duration + delta) } : s));
  };

  const handleSaveStop = (data) => {
    if (editingStop) {
      // Update existing
      updateStops(stops.map(s => s.id === editingStop.id ? { ...s, ...data } : s));
    } else {
      // Add new
      const newStop = {
        id: `new-${Date.now()}`,
        ...data,
        startTime: '09:00', 
        location: { lat: 0, lng: 0 }
      };
      updateStops([...stops, newStop]);
    }
  };

  const handleEditDay = (day) => {
    setEditingDay(day);
    setDayModalOpen(true);
  };

  const handleUpdateDay = (newLabel, newDate) => {
    const targetId = editingDay?.id || activeDayId;
    const newDays = trip.days.map(d => d.id === targetId ? { ...d, label: newLabel, date: newDate } : d);
    setTrip({ ...trip, days: newDays });
  };

  const handleAddDay = () => {
    const lastDay = trip.days[trip.days.length - 1];
    // Simple date increment logic
    const dateObj = new Date(lastDay.date);
    dateObj.setDate(dateObj.getDate() + 1);
    const nextDate = dateObj.toISOString().split('T')[0];

    const newDayId = `day-${trip.days.length + 1}`;
    const newDay = {
      id: newDayId,
      date: nextDate,
      label: `Day ${trip.days.length + 1}`,
      stops: []
    };

    setTrip(prev => ({ ...prev, days: [...prev.days, newDay] }));
    setActiveDayId(newDayId);
  };

  const handleGenerateItinerary = (generatedStops) => {
    // Add IDs to generated stops
    const newStops = generatedStops.map(stop => ({
      id: `ai-${Date.now()}-${Math.random()}`,
      startTime: '09:00', // Will be recalculated
      location: { lat: 0, lng: 0 },
      ...stop
    }));
    
    // Replace current day's stops with generated ones
    updateStops(newStops);
  };

  const handleEnrichStop = async (stop) => {
    const prompt = `Give me one interesting, insider travel tip, fun fact, or "must-eat" recommendation for "${stop.name}". Keep it short (max 20 words).`;
    const tip = await generateGeminiContent(prompt);
    if (tip) {
      const currentRemarks = stop.remarks || "";
      const separator = currentRemarks ? "\n" : "";
      const newRemarks = `${currentRemarks}${separator}✨ Tip: ${tip}`;
      
      updateStops(stops.map(s => s.id === stop.id ? { ...s, remarks: newRemarks } : s));
    }
  };

  const updateStops = (newStops) => {
    const newDays = trip.days.map(day => 
      day.id === activeDayId ? { ...day, stops: newStops } : day
    );
    setTrip({ ...trip, days: newDays });
  };

  return (
    <div className="h-screen w-full bg-gray-50 flex flex-col font-sans text-slate-800">
      <Header 
        title={trip.title} 
        days={trip.days} 
        activeDayId={activeDayId} 
        onEditDay={handleEditDay}
      />
      
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Panel: Itinerary List */}
        <div className={`${viewMode === 'map' ? 'hidden md:flex' : 'flex'} flex-col w-full md:w-[480px] bg-white border-r border-gray-200 z-10 shadow-xl`}>
          <DayTabs 
            days={trip.days} 
            activeDayId={activeDayId} 
            setActiveDayId={setActiveDayId} 
            onAddDay={handleAddDay}
            onEditDay={handleEditDay}
            onOpenAI={() => setAiModalOpen(true)}
          />
          
          <div className="flex-1 overflow-y-auto p-4 scroll-smooth">
            <div className="max-w-md mx-auto">
              {scheduledStops.map((stop, index) => (
                <StopCard 
                  key={stop.id} 
                  stop={stop} 
                  index={index}
                  isLast={index === scheduledStops.length - 1}
                  onMoveUp={(i) => handleMoveStop(i, -1)}
                  onMoveDown={(i) => handleMoveStop(i, 1)}
                  onDelete={handleDeleteStop}
                  onChangeDuration={handleChangeDuration}
                  onEdit={(stop) => { setEditingStop(stop); setStopModalOpen(true); }}
                  onEnrich={handleEnrichStop}
                />
              ))}
              
              <AddStopButton onClick={() => { setEditingStop(null); setStopModalOpen(true); }} />
              <div className="h-20"></div> 
            </div>
          </div>
          
          <div className="md:hidden absolute bottom-6 right-6 z-30">
             <button 
               onClick={() => setViewMode(viewMode === 'list' ? 'map' : 'list')}
               className="bg-gray-900 text-white p-4 rounded-full shadow-xl flex items-center gap-2"
             >
               {viewMode === 'list' ? <Map size={20} /> : <Navigation size={20} />}
               <span className="font-bold">{viewMode === 'list' ? 'Map' : 'List'}</span>
             </button>
          </div>
        </div>

        {/* Right Panel: Map */}
        <div className={`${viewMode === 'list' ? 'hidden md:block' : 'block'} flex-1 bg-gray-100 relative`}>
          <SchematicMap stops={scheduledStops} activeDay={activeDay} />
          <div className="absolute top-4 right-4 flex flex-col gap-2">
            <button className="w-10 h-10 bg-white rounded-lg shadow-md flex items-center justify-center text-gray-600 hover:text-emerald-600">
              <Plus size={20} />
            </button>
             <button className="w-10 h-10 bg-white rounded-lg shadow-md flex items-center justify-center text-gray-600 hover:text-emerald-600">
              <Navigation size={20} />
            </button>
          </div>
        </div>
      </div>

      <StopModal 
        isOpen={stopModalOpen} 
        onClose={() => setStopModalOpen(false)} 
        onSave={handleSaveStop}
        initialData={editingStop}
      />

      <DayEditModal
        isOpen={dayModalOpen}
        onClose={() => setDayModalOpen(false)}
        onSave={handleUpdateDay}
        initialData={editingDay || activeDay}
      />

      <AIPlannerModal 
        isOpen={aiModalOpen}
        onClose={() => setAiModalOpen(false)}
        onGenerate={handleGenerateItinerary}
      />
    </div>
  );
}
