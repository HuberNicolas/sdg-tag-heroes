export interface FacultySchemaBase {
  facultyId: number;
  facultyName: string;
}

export interface FacultySchemaFull extends FacultySchemaBase {
  facultySetSpec: string;
  createdAt: string;
  updatedAt: string;
}
