export interface AuthorSchemaBase {
  author_id: number;
  orcid_id?: string;
}

export interface AuthorSchemaFull extends AuthorSchemaBase {
  name?: string;
  lastname?: string;
  surname?: string;
  created_at: string;
  updated_at: string;
}
