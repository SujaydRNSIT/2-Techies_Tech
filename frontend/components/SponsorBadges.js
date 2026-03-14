import { 
  Shield, 
  Search, 
  Link, 
  CreditCard, 
  Activity, 
  Bot, 
  Database, 
  MessageSquare 
} from 'lucide-react';

const sponsors = [
  { name: 'Crustdata', icon: Database, description: 'Merchant Verification', color: 'bg-blue-100 text-blue-800' },
  { name: 'SafeDep', icon: Shield, description: 'File Security Scan', color: 'bg-green-100 text-green-800' },
  { name: 'Gearsec', icon: Link, description: 'URL Threat Detection', color: 'bg-purple-100 text-purple-800' },
  { name: 'Razorpay', icon: CreditCard, description: 'Payment Execution', color: 'bg-indigo-100 text-indigo-800' },
  { name: 'S2.dev', icon: Activity, description: 'Event Streaming', color: 'bg-orange-100 text-orange-800' },
  { name: 'Emergent', icon: Bot, description: 'Agent Orchestration', color: 'bg-cyan-100 text-cyan-800' },
  { name: 'Unsiloed', icon: Search, description: 'Knowledge Retrieval', color: 'bg-pink-100 text-pink-800' },
  { name: 'Concierge', icon: MessageSquare, description: 'Response Automation', color: 'bg-teal-100 text-teal-800' },
];

export default function SponsorBadges() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {sponsors.map((sponsor) => {
        const Icon = sponsor.icon;
        return (
          <div
            key={sponsor.name}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg ${sponsor.color} text-xs font-medium`}
          >
            <Icon className="w-4 h-4" />
            <div className="flex flex-col">
              <span className="font-semibold">{sponsor.name}</span>
              <span className="opacity-75 text-[10px]">{sponsor.description}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
