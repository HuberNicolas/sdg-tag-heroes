import { UserRole } from "../../enums/enums";

export interface UserSchemaBase {
  userId: number;
  nickname?: string | null;
  email: string;
  isActive: boolean;
  roles: UserRole[];
}

export interface UserSchemaFull extends UserSchemaBase {
  createdAt: string;
  updatedAt: string;
}
