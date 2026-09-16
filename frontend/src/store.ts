import { atom } from 'jotai';

export interface UserProfile {
  name: string;
  email: string;
  picture: string;
}

export interface GoogleCredentials {
  access_token: string;
  refresh_token: string;
  token_uri: string;
  client_id: string;
  client_secret: string;
  scopes: string[];
}

export const userAtom = atom<UserProfile | null>(null);
export const googleCredentialsAtom = atom<GoogleCredentials | null>(null);
