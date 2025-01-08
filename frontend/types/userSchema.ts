export interface UserSchema {
  user_id: number;
  email: string;
  roles: string[];
  is_active: boolean;
}
