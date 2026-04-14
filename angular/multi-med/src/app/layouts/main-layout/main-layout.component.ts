import { Component, HostListener, OnInit } from '@angular/core';
import { RouterOutlet, RouterModule, Router } from '@angular/router';
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
    { titulo: 'Dashboard/Agenda', rota: '/dashboard', icone: 'event', showOnMobile: true, perfis: ['medico', 'funcionario', 'paciente'] },
    { titulo: 'Prontuário PEP', rota: '/pep', icone: 'medical_services', showOnMobile: false, perfis: ['medico'] },
  ];

  filteredMenu: MenuItem[] = [];

  constructor(private router: Router) {}

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

  logout() {
    localStorage.removeItem('token');
    this.router.navigate(['/login']);
  }
}
