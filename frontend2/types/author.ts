export interface AuthorSchemaBase {
  authorId: number;
  orcidId?: string | null;
  name?: string | null;
  lastname?: string | null;
  surname?: string | null;
}

export interface AuthorSchemaFull extends AuthorSchemaBase {
  createdAt: string;
  updatedAt: string;
}
