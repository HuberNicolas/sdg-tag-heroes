import { SDGXPBankHistorySchemaBase, SDGXPBankHistorySchemaFull } from "./sdgXPBankHistory";

export interface SDGXPBankSchemaBase {
  sdgXpBankId: number;
  userId: number;
  totalXp: number;
  sdg1Xp: number;
  sdg2Xp: number;
  sdg3Xp: number;
  sdg4Xp: number;
  sdg5Xp: number;
  sdg6Xp: number;
  sdg7Xp: number;
  sdg8Xp: number;
  sdg9Xp: number;
  sdg10Xp: number;
  sdg11Xp: number;
  sdg12Xp: number;
  sdg13Xp: number;
  sdg14Xp: number;
  sdg15Xp: number;
  sdg16Xp: number;
  sdg17Xp: number;
  histories: (SDGXPBankHistorySchemaBase | SDGXPBankHistorySchemaFull)[];
}

export interface SDGXPBankSchemaFull extends SDGXPBankSchemaBase {
  createdAt: string;
  updatedAt: string;
}
