export interface SDGCoinWalletHistorySchemaBase {
  historyId: number;
  walletId: number;
  increment: number;
  reason?: string | null;
  isShown?: boolean | null;
  timestamp: string; // ISO date string
}

export interface SDGCoinWalletHistorySchemaFull extends SDGCoinWalletHistorySchemaBase {
  createdAt: string;
  updatedAt: string;
}
