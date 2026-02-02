"use client";

import { useState, useMemo, useRef } from "react";
import {
  Menu,
  Search,
  Bell,
  ChevronDown,
  Building2,
  AlertTriangle,
  BarChart3,
  Settings,
  Plus,
  X,
  Copy,
  Send,
  User,
  HelpCircle,
  Grid3X3,
  Calendar,
  MessageSquare,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
  Cell,
} from "recharts";
import { OrchestrateChatEmbed, OrchestrateChatEmbedHandle } from "@/components/OrchestrateChatEmbed";
import { useToast } from "@/hooks/use-toast";
import { Clipboard, Clock, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

// Types
interface Incident {
  id: string;
  title: string;
  service: string;
  severity: "P1" | "P2" | "P3" | "P4";
  status: "Open" | "Resolved";
  opened: string;
  resolved: string | null;
  owner: string;
  description: string;
}

interface TriageOutcome {
  id: string;
  incidentId: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  action?: string;
  timestamp: string;
}

// Initial mock triage outcomes
const initialTriageOutcomes: TriageOutcome[] = [
  {
    id: "TRG-001",
    incidentId: "INC-2024-001",
    status: "completed",
    action: "Auto-resolved: Restarted payment gateway service",
    timestamp: "2024-01-28 11:40",
  },
  {
    id: "TRG-002",
    incidentId: "INC-2024-003",
    status: "completed",
    action: "Escalated to L2: Consumer lag requires scaling",
    timestamp: "2024-01-26 09:15",
  },
  {
    id: "TRG-003",
    incidentId: "INC-2024-004",
    status: "completed",
    action: "Auto-resolved: Refreshed JWT signing keys",
    timestamp: "2024-01-26 00:30",
  },
  {
    id: "TRG-004",
    incidentId: "INC-2024-006",
    status: "completed",
    action: "Auto-resolved: Increased connection pool size",
    timestamp: "2024-01-23 12:45",
  },
];

// Mock data
const initialIncidents: Incident[] = [
  {
    id: "INC-2024-001",
    title: "Payment gateway timeout errors",
    service: "Payments DB",
    severity: "P1",
    status: "Resolved",
    opened: "2024-01-28 09:15",
    resolved: "2024-01-28 11:45",
    owner: "Sarah Chen",
    description: "Multiple timeout errors occurring during payment processing. Customers unable to complete transactions.",
  },
  {
    id: "INC-2024-002",
    title: "API rate limiting not enforced",
    service: "API Gateway",
    severity: "P2",
    status: "Resolved",
    opened: "2024-01-27 14:30",
    resolved: "2024-01-27 16:00",
    owner: "Marcus Johnson",
    description: "Rate limiting rules not being applied correctly, allowing excessive API calls.",
  },
  {
    id: "INC-2024-003",
    title: "Kafka consumer lag spike",
    service: "Kafka",
    severity: "P2",
    status: "Resolved",
    opened: "2024-01-26 08:00",
    resolved: "2024-01-26 10:30",
    owner: "Emily Rodriguez",
    description: "Consumer groups experiencing significant lag, causing delayed message processing.",
  },
  {
    id: "INC-2024-004",
    title: "Auth token validation failures",
    service: "Auth Service",
    severity: "P1",
    status: "Resolved",
    opened: "2024-01-25 22:45",
    resolved: "2024-01-26 01:15",
    owner: "David Kim",
    description: "JWT token validation failing intermittently, causing user authentication issues.",
  },
  {
    id: "INC-2024-005",
    title: "Batch job memory overflow",
    service: "Batch Jobs",
    severity: "P3",
    status: "Resolved",
    opened: "2024-01-24 03:00",
    resolved: "2024-01-24 06:30",
    owner: "Lisa Wang",
    description: "Nightly batch processing job running out of memory on large datasets.",
  },
  {
    id: "INC-2024-006",
    title: "Database connection pool exhausted",
    service: "Payments DB",
    severity: "P1",
    status: "Resolved",
    opened: "2024-01-23 11:20",
    resolved: "2024-01-23 13:00",
    owner: "Sarah Chen",
    description: "Connection pool reaching maximum capacity during peak hours.",
  },
  {
    id: "INC-2024-007",
    title: "SSL certificate expiration warning",
    service: "API Gateway",
    severity: "P4",
    status: "Resolved",
    opened: "2024-01-22 09:00",
    resolved: "2024-01-22 09:30",
    owner: "Marcus Johnson",
    description: "SSL certificate for API endpoint expiring in 7 days.",
  },
  {
    id: "INC-2024-008",
    title: "Message serialization errors",
    service: "Kafka",
    severity: "P3",
    status: "Resolved",
    opened: "2024-01-21 15:45",
    resolved: "2024-01-21 17:30",
    owner: "Emily Rodriguez",
    description: "Avro schema mismatch causing serialization failures for new message types.",
  },
  {
    id: "INC-2024-009",
    title: "OAuth provider connectivity issues",
    service: "Auth Service",
    severity: "P2",
    status: "Resolved",
    opened: "2024-01-20 10:00",
    resolved: "2024-01-20 11:45",
    owner: "David Kim",
    description: "Intermittent connectivity to external OAuth providers affecting social login.",
  },
  {
    id: "INC-2024-010",
    title: "Report generation timeout",
    service: "Batch Jobs",
    severity: "P4",
    status: "Resolved",
    opened: "2024-01-19 07:30",
    resolved: "2024-01-19 09:00",
    owner: "Lisa Wang",
    description: "Monthly report generation exceeding timeout threshold for large accounts.",
  },
];

const mttrData = [
  { day: "Mon", mttr: 2.1 },
  { day: "Tue", mttr: 1.8 },
  { day: "Wed", mttr: 2.5 },
  { day: "Thu", mttr: 1.5 },
  { day: "Fri", mttr: 1.9 },
  { day: "Sat", mttr: 2.2 },
  { day: "Sun", mttr: 1.7 },
];

const severityData = [
  { severity: "P1", count: 3 },
  { severity: "P2", count: 4 },
  { severity: "P3", count: 2 },
  { severity: "P4", count: 2 },
];

// Uptime data by service (last 30 days)
const uptimeData = [
  { service: "Payments DB", uptime: 99.2, downtime: 0.8, slaTarget: 99.9 },
  { service: "API Gateway", uptime: 99.8, downtime: 0.2, slaTarget: 99.9 },
  { service: "Kafka", uptime: 99.5, downtime: 0.5, slaTarget: 99.5 },
  { service: "Auth Service", uptime: 99.7, downtime: 0.3, slaTarget: 99.9 },
  { service: "Batch Jobs", uptime: 98.9, downtime: 1.1, slaTarget: 99.0 },
];

// SLA compliance trend (last 6 months)
const slaComplianceData = [
  { month: "Aug", compliance: 98.2, target: 99.5 },
  { month: "Sep", compliance: 99.1, target: 99.5 },
  { month: "Oct", compliance: 99.4, target: 99.5 },
  { month: "Nov", compliance: 98.8, target: 99.5 },
  { month: "Dec", compliance: 99.6, target: 99.5 },
  { month: "Jan", compliance: 99.3, target: 99.5 },
];

// Incident trend data (last 12 weeks)
const incidentTrendData = [
  { week: "W1", p1: 1, p2: 2, p3: 3, p4: 2 },
  { week: "W2", p1: 0, p2: 3, p3: 2, p4: 4 },
  { week: "W3", p1: 2, p2: 1, p3: 4, p4: 1 },
  { week: "W4", p1: 0, p2: 2, p3: 2, p4: 3 },
  { week: "W5", p1: 1, p2: 1, p3: 3, p4: 2 },
  { week: "W6", p1: 0, p2: 2, p3: 1, p4: 4 },
  { week: "W7", p1: 1, p2: 3, p3: 2, p4: 1 },
  { week: "W8", p1: 0, p2: 1, p3: 4, p4: 2 },
  { week: "W9", p1: 2, p2: 2, p3: 1, p4: 3 },
  { week: "W10", p1: 0, p2: 1, p3: 3, p4: 2 },
  { week: "W11", p1: 1, p2: 2, p3: 2, p4: 1 },
  { week: "W12", p1: 0, p2: 1, p3: 2, p4: 2 },
];

const services = ["Payments DB", "API Gateway", "Kafka", "Auth Service", "Batch Jobs"];
const severities: Array<"P1" | "P2" | "P3" | "P4"> = ["P1", "P2", "P3", "P4"];

// Severity badge colors
function getSeverityColor(severity: string) {
  switch (severity) {
    case "P1":
      return "bg-red-100 text-red-700 border-red-200";
    case "P2":
      return "bg-orange-100 text-orange-700 border-orange-200";
    case "P3":
      return "bg-yellow-100 text-yellow-700 border-yellow-200";
    case "P4":
      return "bg-blue-100 text-blue-700 border-blue-200";
    default:
      return "bg-gray-100 text-gray-700 border-gray-200";
  }
}

function getStatusColor(status: string) {
  return status === "Resolved"
    ? "bg-green-100 text-green-700 border-green-200"
    : "bg-blue-100 text-blue-700 border-blue-200";
}

// Nav items
const navItems = [
  { icon: Building2, label: "Build", active: false },
  { icon: AlertTriangle, label: "Incidents", active: true },
  { icon: BarChart3, label: "Analytics", active: false },
  { icon: Settings, label: "Settings", active: false },
];

export default function Dashboard() {
  const [incidents, setIncidents] = useState<Incident[]>(initialIncidents);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [triageOutcomes, setTriageOutcomes] = useState<TriageOutcome[]>(initialTriageOutcomes);

  // Ref for the chat embed component
  const chatEmbedRef = useRef<OrchestrateChatEmbedHandle>(null);

  // Toast hook for notifications
  const { toast } = useToast();

  // Create incident form state
  const [newIncident, setNewIncident] = useState({
    title: "",
    service: "",
    severity: "" as "P1" | "P2" | "P3" | "P4" | "",
    description: "",
  });

  // Filter incidents
  const filteredIncidents = useMemo(() => {
    return incidents.filter((incident) => {
      const matchesStatus =
        statusFilter === "all" || incident.status === statusFilter;
      const matchesSeverity =
        severityFilter === "all" || incident.severity === severityFilter;
      const matchesSearch =
        searchQuery === "" ||
        incident.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        incident.id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesStatus && matchesSeverity && matchesSearch;
    });
  }, [incidents, statusFilter, severityFilter, searchQuery]);

  // Handle row click
  const handleRowClick = (incident: Incident) => {
    setSelectedIncident(incident);
    setIsDrawerOpen(true);
  };

  // Handle create incident
  const handleCreateIncident = () => {
    if (!newIncident.title || !newIncident.service || !newIncident.severity) {
      return;
    }

    const incident: Incident = {
      id: `INC-2024-${String(incidents.length + 1).padStart(3, "0")}`,
      title: newIncident.title,
      service: newIncident.service,
      severity: newIncident.severity,
      status: "Open",
      opened: new Date().toISOString().slice(0, 16).replace("T", " "),
      resolved: null,
      owner: "Current User",
      description: newIncident.description,
    };

    setIncidents([incident, ...incidents]);
    setSelectedIncident(incident);
    setIsDrawerOpen(true);
    setNewIncident({ title: "", service: "", severity: "", description: "" });
  };

  // Format incident for AEGIS
  const formatIncidentForAegis = (incident: Incident) => {
    return `Incident ${incident.id}: ${incident.title}\nService: ${incident.service}\nSeverity: ${incident.severity}\nDescription: ${incident.description}`;
  };

  // Handle send to AEGIS
  const handleSendToAegis = async (incident: Incident) => {
    const formattedText = formatIncidentForAegis(incident);

    // Copy to clipboard first (always works)
    let clipboardSuccess = false;
    try {
      await navigator.clipboard.writeText(formattedText);
      clipboardSuccess = true;
    } catch (err) {
      console.error("Failed to copy to clipboard:", err);
    }

    // Open chat panel if closed
    if (!isChatOpen) {
      setIsChatOpen(true);
    }

    // Add a pending triage outcome
    const newOutcome: TriageOutcome = {
      id: `TRG-${String(triageOutcomes.length + 1).padStart(3, "0")}`,
      incidentId: incident.id,
      status: "pending",
      timestamp: new Date().toISOString().slice(0, 16).replace("T", " "),
    };
    setTriageOutcomes([newOutcome, ...triageOutcomes]);

    // Best effort: Try to auto-fill the chat input
    // Give a small delay for the chat to open/render
    setTimeout(() => {
      const autoFillSuccess = chatEmbedRef.current?.tryAutoFill(formattedText);

      if (autoFillSuccess) {
        toast({
          title: "Incident sent to AEGIS",
          description: `${incident.id} has been loaded into the chat. Press Enter to submit.`,
        });
      } else if (clipboardSuccess) {
        toast({
          title: "Incident copied to clipboard",
          description: `${incident.id} is ready to paste into AEGIS chat (Ctrl+V).`,
        });
      } else {
        toast({
          title: "Ready for triage",
          description: `Please manually enter ${incident.id} details into the chat.`,
        });
      }
    }, 300);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Top Bar */}
      <header className="sticky top-0 z-50 h-12 bg-sidebar border-b border-sidebar-border flex items-center px-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" className="text-sidebar-foreground hover:bg-sidebar-accent">
            <Menu className="h-5 w-5" />
          </Button>
          <img 
            src="/blueshift-logo.png" 
            alt="Team BlueShift" 
            className="h-10 w-auto object-contain"
          />
        </div>

        <div className="flex-1 flex justify-center px-8">
          <div className="relative w-full max-w-xl">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search resources and products..."
              className="pl-9 bg-sidebar-accent border-sidebar-border text-sidebar-foreground placeholder:text-muted-foreground h-8"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" className="text-sidebar-foreground hover:bg-sidebar-accent gap-2">
            <span className="text-xs">A.E.G.I.S</span>
            <ChevronDown className="h-3 w-3" />
          </Button>
          <Button variant="ghost" size="icon" className="text-sidebar-foreground hover:bg-sidebar-accent">
            <HelpCircle className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="text-sidebar-foreground hover:bg-sidebar-accent">
            <Grid3X3 className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="text-sidebar-foreground hover:bg-sidebar-accent">
            <Calendar className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="text-sidebar-foreground hover:bg-sidebar-accent relative">
            <Bell className="h-4 w-4" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-primary rounded-full" />
          </Button>
          <Button variant="ghost" size="icon" className="text-sidebar-foreground hover:bg-sidebar-accent">
            <User className="h-4 w-4" />
          </Button>
        </div>
      </header>

      <div className="flex">
        {/* Left Navigation Rail */}
        <aside className="w-12 bg-sidebar border-r border-sidebar-border flex flex-col items-center py-4 gap-2">
          {navItems.map((item) => (
            <Button
              key={item.label}
              variant="ghost"
              size="icon"
              className={`text-sidebar-foreground hover:bg-sidebar-accent ${
                item.active ? "bg-sidebar-accent" : ""
              }`}
              title={item.label}
            >
              <item.icon className="h-5 w-5" />
            </Button>
          ))}
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-auto">
          {/* Page Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>
              <ChevronDown className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" className="text-muted-foreground">
                Edit dashboard
              </Button>
              <Button size="sm" className="gap-2">
                <Plus className="h-4 w-4" />
                Create resource
              </Button>
            </div>
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 xl:grid-cols-[1fr_400px] gap-6">
            {/* Left Column */}
            <div className="space-y-6">
              {/* Incident List Card */}
              <Card>
                <CardHeader className="pb-4">
                  <CardTitle className="text-base font-medium">Resolved incidents</CardTitle>
                </CardHeader>
                <CardContent>
                  {/* Filters */}
                  <div className="flex flex-wrap gap-3 mb-4">
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                      <SelectTrigger className="w-[140px] h-8 text-sm">
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="Open">Open</SelectItem>
                        <SelectItem value="Resolved">Resolved</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={severityFilter} onValueChange={setSeverityFilter}>
                      <SelectTrigger className="w-[140px] h-8 text-sm">
                        <SelectValue placeholder="Severity" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Severity</SelectItem>
                        {severities.map((sev) => (
                          <SelectItem key={sev} value={sev}>
                            {sev}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <div className="relative flex-1 min-w-[200px]">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search by title or ID..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9 h-8 text-sm"
                      />
                    </div>
                  </div>

                  {/* Table */}
                  <div className="border rounded overflow-hidden">
                    <Table>
                      <TableHeader>
                        <TableRow className="bg-muted/50">
                          <TableHead className="text-xs font-medium">Incident ID</TableHead>
                          <TableHead className="text-xs font-medium">Title</TableHead>
                          <TableHead className="text-xs font-medium">Service</TableHead>
                          <TableHead className="text-xs font-medium">Severity</TableHead>
                          <TableHead className="text-xs font-medium">Status</TableHead>
                          <TableHead className="text-xs font-medium">Opened</TableHead>
                          <TableHead className="text-xs font-medium">Resolved</TableHead>
                          <TableHead className="text-xs font-medium">Owner</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredIncidents.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                              No incidents match your filters.
                            </TableCell>
                          </TableRow>
                        ) : (
                          filteredIncidents.map((incident) => (
                            <TableRow
                              key={incident.id}
                              className="cursor-pointer hover:bg-muted/50 transition-colors"
                              onClick={() => handleRowClick(incident)}
                            >
                              <TableCell className="text-xs font-mono text-primary">
                                {incident.id}
                              </TableCell>
                              <TableCell className="text-xs max-w-[200px] truncate">
                                {incident.title}
                              </TableCell>
                              <TableCell className="text-xs">{incident.service}</TableCell>
                              <TableCell>
                                <Badge
                                  variant="outline"
                                  className={`text-xs ${getSeverityColor(incident.severity)}`}
                                >
                                  {incident.severity}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge
                                  variant="outline"
                                  className={`text-xs ${getStatusColor(incident.status)}`}
                                >
                                  {incident.status}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-xs text-muted-foreground">
                                {incident.opened}
                              </TableCell>
                              <TableCell className="text-xs text-muted-foreground">
                                {incident.resolved || "—"}
                              </TableCell>
                              <TableCell className="text-xs">{incident.owner}</TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>

              {/* Create Incident Card */}
              <Card>
                <CardHeader className="pb-4">
                  <CardTitle className="text-base font-medium">Create incident</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="title" className="text-xs">
                        Title
                      </Label>
                      <Input
                        id="title"
                        placeholder="Enter incident title"
                        value={newIncident.title}
                        onChange={(e) =>
                          setNewIncident({ ...newIncident, title: e.target.value })
                        }
                        className="h-8 text-sm"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="service" className="text-xs">
                        Service
                      </Label>
                      <Select
                        value={newIncident.service}
                        onValueChange={(value) =>
                          setNewIncident({ ...newIncident, service: value })
                        }
                      >
                        <SelectTrigger className="h-8 text-sm">
                          <SelectValue placeholder="Select service" />
                        </SelectTrigger>
                        <SelectContent>
                          {services.map((service) => (
                            <SelectItem key={service} value={service}>
                              {service}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="severity" className="text-xs">
                        Severity
                      </Label>
                      <Select
                        value={newIncident.severity}
                        onValueChange={(value) =>
                          setNewIncident({
                            ...newIncident,
                            severity: value as "P1" | "P2" | "P3" | "P4",
                          })
                        }
                      >
                        <SelectTrigger className="h-8 text-sm">
                          <SelectValue placeholder="Select severity" />
                        </SelectTrigger>
                        <SelectContent>
                          {severities.map((sev) => (
                            <SelectItem key={sev} value={sev}>
                              {sev}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="description" className="text-xs">
                        Description
                      </Label>
                      <Textarea
                        id="description"
                        placeholder="Describe the incident..."
                        value={newIncident.description}
                        onChange={(e) =>
                          setNewIncident({ ...newIncident, description: e.target.value })
                        }
                        className="text-sm min-h-[80px]"
                      />
                    </div>
                  </div>

                  <Button
                    onClick={handleCreateIncident}
                    className="mt-4"
                    size="sm"
                    disabled={!newIncident.title || !newIncident.service || !newIncident.severity}
                  >
                    Create incident
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* AEGIS Triage Card */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <MessageSquare className="h-4 w-4" />
                    AEGIS Triage (watsonx Orchestrate)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground mb-3">
                    Paste an incident or click &quot;Send to AEGIS&quot; from a selected incident.
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsChatOpen(!isChatOpen)}
                    className="w-full"
                  >
                    {isChatOpen ? "Close embedded chat" : "Open embedded chat"}
                  </Button>

                  {isChatOpen && (
                    <div className="mt-4 space-y-3">
                      {/* Hint bar */}
                      <div className="flex items-center gap-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
                        <Clipboard className="h-3.5 w-3.5 flex-shrink-0" />
                        <span>Tip: Click &quot;Send to AEGIS&quot; to auto-fill, or paste with Ctrl+V.</span>
                      </div>
                      {/* Embedded AEGIS Chat */}
                      <OrchestrateChatEmbed ref={chatEmbedRef} />
                    </div>
                  )}
                </CardContent>
              </Card>
                            
              {/* Service Uptime / Downtime Chart */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Service Uptime (last 30 days)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[180px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={uptimeData}
                        layout="vertical"
                        margin={{ left: 20 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={false} />
                        <XAxis
                          type="number"
                          domain={[96, 100]}
                          tick={{ fontSize: 10 }}
                          stroke="#9ca3af"
                          tickFormatter={(v) => `${v}%`}
                        />
                        <YAxis
                          type="category"
                          dataKey="service"
                          tick={{ fontSize: 9 }}
                          stroke="#9ca3af"
                          width={70}
                        />
                        <Tooltip
                          contentStyle={{
                            fontSize: 12,
                            backgroundColor: "white",
                            border: "1px solid #e5e7eb",
                          }}
                          formatter={(value: number, name: string) => [
                            `${value.toFixed(2)}%`,
                            name === "uptime" ? "Uptime" : "Downtime",
                          ]}
                        />
                        <Bar dataKey="uptime" stackId="a" fill="#22c55e" radius={[0, 2, 2, 0]} name="Uptime">
                          {uptimeData.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={entry.uptime >= entry.slaTarget ? "#22c55e" : "#f97316"}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <span className="w-3 h-3 rounded-sm bg-green-500" />
                      <span>Meeting SLA</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="w-3 h-3 rounded-sm bg-orange-500" />
                      <span>Below SLA</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* SLA Compliance Trend */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">SLA Compliance Trend (6 months)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[160px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={slaComplianceData}>
                        <defs>
                          <linearGradient id="complianceGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#0f62fe" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#0f62fe" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="month" tick={{ fontSize: 10 }} stroke="#9ca3af" />
                        <YAxis
                          domain={[97, 100]}
                          tick={{ fontSize: 10 }}
                          stroke="#9ca3af"
                          tickFormatter={(v) => `${v}%`}
                        />
                        <Tooltip
                          contentStyle={{
                            fontSize: 12,
                            backgroundColor: "white",
                            border: "1px solid #e5e7eb",
                          }}
                          formatter={(value: number) => [`${value.toFixed(1)}%`]}
                        />
                        <ReferenceLine
                          y={99.5}
                          stroke="#dc2626"
                          strokeDasharray="4 4"
                          label={{
                            value: "SLA Target",
                            position: "insideTopRight",
                            fontSize: 9,
                            fill: "#dc2626",
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="compliance"
                          stroke="#0f62fe"
                          strokeWidth={2}
                          fill="url(#complianceGradient)"
                          name="Compliance"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Incident Trend by Severity (12 weeks) */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Incident Trend (12 weeks)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[160px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={incidentTrendData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="week" tick={{ fontSize: 9 }} stroke="#9ca3af" />
                        <YAxis tick={{ fontSize: 10 }} stroke="#9ca3af" />
                        <Tooltip
                          contentStyle={{
                            fontSize: 12,
                            backgroundColor: "white",
                            border: "1px solid #e5e7eb",
                          }}
                        />
                        <Legend
                          iconSize={8}
                          wrapperStyle={{ fontSize: 10 }}
                        />
                        <Bar dataKey="p1" stackId="a" fill="#dc2626" name="P1" />
                        <Bar dataKey="p2" stackId="a" fill="#f97316" name="P2" />
                        <Bar dataKey="p3" stackId="a" fill="#eab308" name="P3" />
                        <Bar dataKey="p4" stackId="a" fill="#3b82f6" name="P4" radius={[2, 2, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* MTTR Chart */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">MTTR (last 7 days)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[140px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={mttrData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="day" tick={{ fontSize: 10 }} stroke="#9ca3af" />
                        <YAxis tick={{ fontSize: 10 }} stroke="#9ca3af" unit="h" />
                        <Tooltip
                          contentStyle={{
                            fontSize: 12,
                            backgroundColor: "white",
                            border: "1px solid #e5e7eb",
                          }}
                          formatter={(value) => [`${value}h`, "MTTR"]}
                        />
                        <Line
                          type="monotone"
                          dataKey="mttr"
                          stroke="#0f62fe"
                          strokeWidth={2}
                          dot={{ fill: "#0f62fe", r: 3 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Incidents by Severity Chart */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Incidents by severity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[140px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={severityData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="severity" tick={{ fontSize: 10 }} stroke="#9ca3af" />
                        <YAxis tick={{ fontSize: 10 }} stroke="#9ca3af" />
                        <Tooltip
                          contentStyle={{
                            fontSize: 12,
                            backgroundColor: "white",
                            border: "1px solid #e5e7eb",
                          }}
                        />
                        <Bar dataKey="count" fill="#0f62fe" radius={[2, 2, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>



              {/* Recent Triage Outcomes Card */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    Recent Triage Outcomes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {triageOutcomes.slice(0, 5).map((outcome) => (
                      <div
                        key={outcome.id}
                        className="flex items-start gap-2 p-2 rounded border bg-muted/30 text-xs"
                      >
                        {outcome.status === "pending" && (
                          <Loader2 className="h-3.5 w-3.5 text-yellow-600 animate-spin flex-shrink-0 mt-0.5" />
                        )}
                        {outcome.status === "in_progress" && (
                          <Loader2 className="h-3.5 w-3.5 text-blue-600 animate-spin flex-shrink-0 mt-0.5" />
                        )}
                        {outcome.status === "completed" && (
                          <CheckCircle2 className="h-3.5 w-3.5 text-green-600 flex-shrink-0 mt-0.5" />
                        )}
                        {outcome.status === "failed" && (
                          <AlertCircle className="h-3.5 w-3.5 text-red-600 flex-shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-mono text-primary font-medium">
                              {outcome.incidentId}
                            </span>
                            <Badge
                              variant="outline"
                              className={
                                outcome.status === "pending"
                                  ? "bg-yellow-100 text-yellow-700 border-yellow-200"
                                  : outcome.status === "in_progress"
                                  ? "bg-blue-100 text-blue-700 border-blue-200"
                                  : outcome.status === "completed"
                                  ? "bg-green-100 text-green-700 border-green-200"
                                  : "bg-red-100 text-red-700 border-red-200"
                              }
                            >
                              {outcome.status === "pending"
                                ? "Pending"
                                : outcome.status === "in_progress"
                                ? "In Progress"
                                : outcome.status === "completed"
                                ? "Completed"
                                : "Failed"}
                            </Badge>
                          </div>
                          {outcome.action && (
                            <p className="text-muted-foreground mt-1 truncate">
                              {outcome.action}
                            </p>
                          )}
                          <p className="text-muted-foreground/70 mt-0.5">
                            {outcome.timestamp}
                          </p>
                        </div>
                      </div>
                    ))}
                    {triageOutcomes.length === 0 && (
                      <p className="text-xs text-muted-foreground text-center py-4">
                        No triage outcomes yet. Send an incident to AEGIS to get started.
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>

      {/* Incident Detail Drawer */}
      <Sheet open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
        <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
          <SheetHeader>
            <SheetTitle className="flex items-center justify-between">
              <span className="font-mono text-primary">{selectedIncident?.id}</span>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsDrawerOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </SheetTitle>
          </SheetHeader>

          {selectedIncident && (
            <div className="mt-6 space-y-6">
              <div>
                <h3 className="text-lg font-medium">{selectedIncident.title}</h3>
                <div className="flex gap-2 mt-2">
                  <Badge
                    variant="outline"
                    className={getSeverityColor(selectedIncident.severity)}
                  >
                    {selectedIncident.severity}
                  </Badge>
                  <Badge
                    variant="outline"
                    className={getStatusColor(selectedIncident.status)}
                  >
                    {selectedIncident.status}
                  </Badge>
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Service</p>
                  <p className="text-sm">{selectedIncident.service}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Owner</p>
                  <p className="text-sm">{selectedIncident.owner}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Opened</p>
                  <p className="text-sm">{selectedIncident.opened}</p>
                </div>
                {selectedIncident.resolved && (
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Resolved</p>
                    <p className="text-sm">{selectedIncident.resolved}</p>
                  </div>
                )}
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Description</p>
                  <p className="text-sm text-muted-foreground">
                    {selectedIncident.description}
                  </p>
                </div>
              </div>

              <Separator />

              <div className="space-y-3">
                <Button
                  className="w-full gap-2"
                  onClick={() => handleSendToAegis(selectedIncident)}
                >
                  <Send className="h-4 w-4" />
                  Send to AEGIS
                </Button>
                <Button
                  variant="outline"
                  className="w-full gap-2 bg-transparent"
                  onClick={async () => {
                    await navigator.clipboard.writeText(
                      formatIncidentForAegis(selectedIncident)
                    );
                  }}
                >
                  <Copy className="h-4 w-4" />
                  Copy incident details
                </Button>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
