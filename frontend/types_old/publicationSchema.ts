import type { AuthorSchemaBase, AuthorSchemaFull } from "~/types/schemas";

export interface PublicationSchemaBase {
  publication_id: number;
}

export interface PublicationSchemaFull extends PublicationSchemaBase {
  oai_identifier: string;
  oai_identifier_num: number;
  title?: string;
  description?: string;
  authors?: Array<AuthorSchemaBase | AuthorSchemaFull>;
  year?: number;
  publisher?: string;
  created_at: string;
  updated_at: string;
}
