"use client";

import {
  Users,
  UserPlus,
  CreditCard,
  BookOpen,
  Globe,
  Briefcase,
  Megaphone,
} from "lucide-react";
import type { ComponentType } from "react";

export const ModuleIconMap: Record<string, ComponentType<any>> = {
  crm: Users,
  people: Users,
  payments: CreditCard,
  training: BookOpen,
  travel: Globe,
  visa: Briefcase,
  marketing: Megaphone,
};

export default ModuleIconMap;
