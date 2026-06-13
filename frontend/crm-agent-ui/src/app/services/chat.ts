import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  sendMessage(message: string, sessionId?: string): Observable<ChatResponse> {
    const body: ChatRequest = {
      message,
      session_id: sessionId
    };
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat`, body);
  }
}