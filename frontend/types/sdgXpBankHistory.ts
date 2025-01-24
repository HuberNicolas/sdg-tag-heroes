import type { SDGType } from "./enums";

export interface SDGXPBankHistorySchemaBase {
  historyId: number;
  xpBankId: number;
  sdg: SDGType;
  increment: number;
  reason?: string | null;
  isShown?: boolean | null;
  timestamp: string;
}

export interface SDGXPBankHistorySchemaFull extends SDGXPBankHistorySchemaBase {
  createdAt: string;
  updatedAt: string;
}
