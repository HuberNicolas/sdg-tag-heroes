import {
  SDGCoinWalletHistorySchemaBase,
  SDGCoinWalletHistorySchemaFull,
} from "./sdgCoinWalletHistory";

export interface SDGCoinWalletSchemaBase {
  sdgCoinWalletId: number;
  userId: number;
  totalCoins: number;
  histories: (SDGCoinWalletHistorySchemaBase | SDGCoinWalletHistorySchemaFull)[];
}

export interface SDGCoinWalletSchemaFull extends SDGCoinWalletSchemaBase {
  createdAt: string;
  updatedAt: string;
}
