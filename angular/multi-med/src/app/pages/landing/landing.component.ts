import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

interface Noticia {
  titulo: string;
  resumo: string;
  data: string;
}

interface ChatMessage {
  origem: 'ia' | 'user';
  texto: string;
}

interface ChatRequest {
  message: string;
  history: { role: string; content: string }[];
  paciente?: string | null;
  opcao_escolhida?: number | null;
  thread_id: number;
}

interface ChatResponse {
  response: string;
  paciente?: string | null;
  opcao_escolhida?: number | null;
}

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterModule, HttpClientModule, FormsModule],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.css'
})
export class LandingComponent implements OnInit {

  noticias: Noticia[] = [];

  // Chat Widget
  isChatOpen: boolean = false;
  chatInput: string = '';
  isTyping: boolean = false;
  chatMessages: ChatMessage[] = [];
  paciente: string | null = null;
  opcao_escolhida: number | null = null;

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.carregarNoticias();
    this.carregarHistoricoChat();
  }

  carregarNoticias() {
    this.http.get<Noticia[]>(`${environment.apiUrl}/noticias`).subscribe({
      next: (res) => {
        this.noticias = res.slice(0, 4);
      },
      error: () => {
        // Fallback se API backend off
        this.noticias = [
          { titulo: 'Nova Ala Cardiológica Inaugurada', resumo: 'A Multi Med orgulha-se de entregar novos equipamentos para diagnósticos do coração de última geração.', data: '12 Abr 2026' },
          { titulo: 'Campanha de Vacinação', resumo: 'Programe e atualize sua carteira de vacinação diretamente nas nossas dependências com agilidade.', data: '05 Abr 2026' },
          { titulo: 'Dicas de Bem Estar', resumo: 'Confira 5 hábitos essenciais que profissionais formados recomendam para manter a longevidade intacta.', data: '22 Mar 2026' }
        ];
      }
    });
  }

  carregarHistoricoChat() {
    this.chatMessages = [
      { origem: 'ia', texto: 'Olá! Sou a assistente virtual da Multi Med. Como posso te ajudar hoje? (ex: "Quero marcar uma consulta")' }
    ];
    this.paciente = null;
    this.opcao_escolhida = null;
  }

  toggleChat() {
    this.isChatOpen = !this.isChatOpen;
  }

  sendMessage() {
    const txt = this.chatInput.trim();
    if (!txt) return;

    this.chatMessages.push({ origem: 'user', texto: txt });
    this.chatInput = '';
    this.isTyping = true;

    // Converter histórico para formato da API
    const history = this.chatMessages.slice(0, -1).map(msg => ({
      role: msg.origem === 'ia' ? 'assistant' : 'user',
      content: msg.texto
    }));

    const req: ChatRequest = {
      message: txt,
      history: history,
      paciente: this.paciente,
      opcao_escolhida: this.opcao_escolhida,
      thread_id: 2
    };

    const chatUrl = environment.apiUrl.replace(/\/api$/, '') + '/chat';

    this.http.post<ChatResponse>(chatUrl, req).subscribe({
      next: (res) => {
        this.isTyping = false;

        if (res.paciente) {
          this.paciente = res.paciente;
        }
        if (res.opcao_escolhida !== undefined && res.opcao_escolhida !== null) {
          this.opcao_escolhida = res.opcao_escolhida;
        }

        this.chatMessages.push({ origem: 'ia', texto: res.response });
      },
      error: (ex: any) => {
        this.isTyping = false;
        const fallbackResponse = this.evaluateSimpleIntent(txt);
        this.chatMessages.push({ origem: 'ia', texto: fallbackResponse });
      }
    });
  }

  // Fallback engine puramente visual se a api local não bater IA.
  evaluateSimpleIntent(text: string): string {
    const low = text.toLowerCase();
    if (low.includes('marcar') || low.includes('agendar')) {
      return 'Entendido! Para marcar sua consulta com segurança e ver a agenda completa, clique no botão superior "Entrar no Sistema". Estarei te esperando lá!';
    }
    if (low.includes('cancelar') || low.includes('confirmar')) {
      return 'Para gerenciar seus agendamentos, será necessário realizar a autenticação. É rapidinho!';
    }
    return 'Sou uma Inteligência focada em atendimento. Aconselho você a Entrar no Sistema para que possamos trocar dados com segurança médica!';
  }
}
