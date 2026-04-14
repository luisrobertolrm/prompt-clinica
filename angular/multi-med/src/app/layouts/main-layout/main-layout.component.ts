import { Component, HostListener, OnInit } from '@angular/core';
import { RouterOutlet, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

interface MenuItem {
  titulo: string;
  rota: string;
  icone: string;
  showOnMobile: boolean;
  perfis: string[];
}

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [RouterOutlet, RouterModule, CommonModule],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.css'
})
export class MainLayoutComponent implements OnInit {
  isMobile: boolean = false;
  isSidebarOpen: boolean = true;
  userProfile = 'medico'; // Mockado
  
  menuItems: MenuItem[] = [
    { titulo: 'Dashboard', rota: '/dashboard', icone: 'dashboard', showOnMobile: true, perfis: ['medico', 'funcionario', 'paciente'] },
    { titulo: 'Prontuário', rota: '/pep', icone: 'medical_services', showOnMobile: false, perfis: ['medico'] },
    { titulo: 'Agenda', rota: '/agenda', icone: 'event', showOnMobile: true, perfis: ['medico', 'funcionario'] }
  ];

  filteredMenu: MenuItem[] = [];

  ngOnInit() {
    this.checkScreenSize();
    this.filterMenu();
  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    this.checkScreenSize();
    this.filterMenu(); // Re-filtra se mudou para mobile
  }

  checkScreenSize() {
    this.isMobile = window.innerWidth <= 768;
    if (this.isMobile) {
      this.isSidebarOpen = false;
    } else {
      this.isSidebarOpen = true; // Maximiza área reativando se voltar a Desktop
    }
  }

  filterMenu() {
    this.filteredMenu = this.menuItems.filter(item => {
      // Regra de perfil
      const hasProfile = item.perfis.includes(this.userProfile);
      // Regra de mobile
      const canShowMobile = this.isMobile ? item.showOnMobile : true;
      return hasProfile && canShowMobile;
    });
  }

  toggleSidebar() {
    this.isSidebarOpen = !this.isSidebarOpen;
  }
}
