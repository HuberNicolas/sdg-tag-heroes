export interface TokenDataSchemaBase {
  user_id: number;
  email: string;
  roles: string[]; // List of roles
}

export interface TokenDataSchemaFull extends TokenDataSchemaBase {
  // No additional fields in the derived schema
}

export interface UserDataSchemaBase {
  user_id: number;
  email: string;
  roles: string[]; // List of roles
}

export interface UserDataSchemaFull extends UserDataSchemaBase {
  login_at?: Date; // Optional datetime field
}

export interface LoginSchemaBase {
  access_token: string;
  token_type: string;
}

export interface LoginSchemaFull extends LoginSchemaBase {
  login_at?: Date; // Optional datetime field
}
