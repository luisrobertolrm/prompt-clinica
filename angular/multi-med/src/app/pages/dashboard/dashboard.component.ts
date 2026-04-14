import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

export interface Consulta {
  id: string;
  horario: string;
  paciente: string;
  tipo: string;
  status: 'Livre' | 'Agendado' | 'Triagem' | 'Em Atendimento' | 'Finalizado';
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  dataAtual: Date = new Date();
  hoje: Date = new Date();
  
  // Fake API de agenda
  agendaTotal: Record<string, Consulta[]> = {
    // A chave é simulada YYYY-MM-DD
  };

  agendaDoDia: Consulta[] = [];

  constructor(private router: Router) {}

  ngOnInit() {
    // Remove o HH:MM:SS para checagens simples de dia
    this.hoje.setHours(0,0,0,0);
    this.dataAtual.setHours(0,0,0,0);
    this.carregarAgenda(this.dataAtual);
  }

  formatDateKey(d: Date): string {
    return d.toISOString().split('T')[0];
  }

  isHoje(): boolean {
    return this.dataAtual.getTime() === this.hoje.getTime();
  }

  mudarDia(deltaDias: number) {
    const novaData = new Date(this.dataAtual);
    novaData.setDate(novaData.getDate() + deltaDias);
    this.dataAtual = novaData;
    this.carregarAgenda(this.dataAtual);
  }

  voltarParaHoje() {
    this.dataAtual = new Date();
    this.dataAtual.setHours(0,0,0,0);
    this.carregarAgenda(this.dataAtual);
  }

  carregarAgenda(data: Date) {
    const key = this.formatDateKey(data);
    
    // Gerador aleatório ou Mock Estático apenas preenchido caso seja "hoje"
    if (this.isHoje()) {
      this.agendaDoDia = [
        { id: 'p01', horario: '08:00', paciente: '', tipo: '', status: 'Livre' },
        { id: 'p02', horario: '08:30', paciente: 'Maria Oliveira', tipo: 'Retorno', status: 'Finalizado' },
        { id: 'p03', horario: '09:00', paciente: 'Carlos Silva', tipo: 'Primeira Vez', status: 'Em Atendimento' },
        { id: 'p04', horario: '09:30', paciente: 'Ana Souza', tipo: 'Exame', status: 'Triagem' },
        { id: 'p05', horario: '10:00', paciente: 'Roberto Dias', tipo: 'Retorno', status: 'Agendado' },
        { id: 'p06', horario: '10:30', paciente: '', tipo: '', status: 'Livre' },
        { id: 'p07', horario: '11:00', paciente: 'Juliana Costa', tipo: 'Primeira Vez', status: 'Agendado' },
      ];
    } else {
      // Se não for hoje, mockar agenda meio vazia
      this.agendaDoDia = [
        { id: 'f01', horario: '08:00', paciente: '', tipo: '', status: 'Livre' },
        { id: 'f02', horario: '08:30', paciente: 'Lucas Macedo', tipo: 'Retorno', status: 'Agendado' },
        { id: 'f03', horario: '09:00', paciente: '', tipo: '', status: 'Livre' }
      ];
    }
  }

  iniciarProntuario(consulta: Consulta) {
    if(consulta.status === 'Livre') return;
    // O sistema real passaria queryParams com o ID!
    this.router.navigate(['/pep']);
  }
}
