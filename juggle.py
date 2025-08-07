import cv2
import numpy as np
import time
from collections import deque
import winsound  # Pour les bips sous Windows

class JuggleCounter:
    def __init__(self):
        # Historique des positions pour analyser la trajectoire
        self.position_history = deque(maxlen=15)  # Garder les 15 dernières positions
        self.y_positions = deque(maxlen=10)       # Positions Y pour détecter montée/descente
        
        # Compteurs et états
        self.juggle_count = 0
        self.total_touches = 0
        self.last_direction = None
        self.direction_changes = 0
        
        # Paramètres de sensibilité
        self.min_movement = 8      # Mouvement minimum pour être considéré
        self.direction_threshold = 3  # Nombre de points pour confirmer une direction
        self.min_height_change = 15   # Changement de hauteur minimum pour un jongle
        
        # État de la session
        self.session_start = time.time()
        self.last_juggle_time = 0
        self.juggle_intervals = []
        
        # Détection de perte de balle
        self.frames_without_ball = 0
        self.max_frames_without_ball = 10
        
        # Bip tous les 10 jongles
        self.last_beep_juggle = 0

    def update(self, ball_position, ball_radius):
        """
        Met à jour le compteur avec une nouvelle position de balle
        """
        current_time = time.time()
        
        if ball_position is None:
            self.frames_without_ball += 1
            # Si on perd la balle trop longtemps, on peut réinitialiser l'état
            if self.frames_without_ball > self.max_frames_without_ball:
                self._reset_trajectory_state()
            return
        
        # Réinitialiser le compteur de frames sans balle
        self.frames_without_ball = 0
        
        # Ajouter la position à l'historique
        x, y = ball_position
        self.position_history.append((x, y, current_time))
        self.y_positions.append(y)
        
        # Analyser la trajectoire si on a assez de points
        if len(self.y_positions) >= 5:
            self._analyze_trajectory(current_time)
    
    def _analyze_trajectory(self, current_time):
        """
        Analyse la trajectoire pour détecter les jongles
        """
        # Calculer la direction actuelle (montée/descente)
        recent_positions = list(self.y_positions)[-5:]  # 5 derniers points
        
        # Calculer la tendance générale
        if len(recent_positions) >= 3:
            # Comparer le début et la fin de la séquence récente
            start_avg = np.mean(recent_positions[:2])
            end_avg = np.mean(recent_positions[-2:])
            
            movement = end_avg - start_avg
            
            # Déterminer la direction avec un seuil pour éviter le bruit
            if movement > self.min_movement:
                current_direction = "down"  # La balle descend (Y augmente)
            elif movement < -self.min_movement:
                current_direction = "up"    # La balle monte (Y diminue)
            else:
                current_direction = self.last_direction  # Pas assez de mouvement
            
            # Détecter un changement de direction significatif
            if (self.last_direction == "down" and current_direction == "up"):
                # La balle était en descente et maintenant elle monte -> JONGLE !
                self._register_juggle(current_time)
                
            elif (self.last_direction == "up" and current_direction == "down"):
                # La balle était en montée et maintenant elle descend -> Pic atteint
                self.total_touches += 1
            
            self.last_direction = current_direction
    
    def _register_juggle(self, current_time):
        """
        Enregistre un nouveau jongle avec BIP tous les 10 jongles
        """
        # Éviter les doubles comptages (trop rapprochés)
        if current_time - self.last_juggle_time > 0.3:  # Au moins 300ms entre jongles
            self.juggle_count += 1
            self.last_juggle_time = current_time
            
            print(f"🏀 Jongle #{self.juggle_count}")
            
            # Calculer l'intervalle avec le jongle précédent
            if len(self.juggle_intervals) > 0:
                interval = current_time - (self.session_start + sum(self.juggle_intervals))
                self.juggle_intervals.append(interval)
                print(f"   Intervalle: {interval:.2f}s")
            else:
                self.juggle_intervals.append(current_time - self.session_start)
            
            # 🔔 BIP TOUS LES 10 JONGLES 🔔
            if self.juggle_count % 10 == 0 and self.juggle_count > self.last_beep_juggle:
                self.last_beep_juggle = self.juggle_count
                try:
                    # Bip plus fort et plus long pour célébrer les 10 jongles
                    winsound.Beep(1500, 500)  # 1500Hz pendant 500ms
                    print(f"🎉 MILESTONE: {self.juggle_count} jongles atteints ! 🎉")
                    print(f"🔔 BIP BIP BIP - FÉLICITATIONS ! 🔔")
                except Exception as e:
                    # Si winsound ne fonctionne pas, print à la place
                    print(f"🔔 BEEP - {self.juggle_count} jongles atteints !")
                    print(f"   (Son indisponible: {e})")
    
    def _reset_trajectory_state(self):
        """
        Réinitialise l'état de trajectoire (quand on perd la balle)
        """
        self.last_direction = None
        # On garde les compteurs, juste l'état de trajectoire
    
    def get_stats(self):
        """
        Retourne les statistiques de la session
        """
        session_duration = time.time() - self.session_start
        
        stats = {
            'jongles': self.juggle_count,
            'touches_totales': self.total_touches,
            'duree_session': session_duration,
            'jongles_par_minute': (self.juggle_count / session_duration * 60) if session_duration > 0 else 0,
            'rythme_moyen': np.mean(self.juggle_intervals) if self.juggle_intervals else 0,
        }
        
        return stats

def detect_yellow_ball(frame):
    """
    Détecte une balle jaune dans l'image - Version optimisée
    """
    # Convertir en HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Plage de couleur jaune (ajustée pour spikeball)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    
    # Créer le masque
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Nettoyer le masque
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Trouver les contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Prendre le plus grand contour
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        if area > 300:  # Seuil minimum
            # Calculer le centre
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Calculer le rayon approximatif
                (x, y), radius = cv2.minEnclosingCircle(largest_contour)
                
                return (cx, cy), int(radius)
    
    return None, 0

def draw_trajectory(frame, counter):
    """
    Dessine la trajectoire récente de la balle avec effet coloré
    """
    if len(counter.position_history) > 1:
        points = [(pos[0], pos[1]) for pos in counter.position_history]
        
        # Dessiner la trajectoire avec dégradé
        for i in range(1, len(points)):
            # Couleur qui s'estompe avec le temps (rouge ancien → vert récent)
            alpha = i / len(points)
            color = (0, int(255 * alpha), int(255 * (1 - alpha)))
            cv2.line(frame, points[i-1], points[i], color, 2)

def draw_hud(frame, counter, ball_pos, ball_radius):
    """
    Dessine l'interface utilisateur (HUD) avec indicateur de milestone
    """
    height, width = frame.shape[:2]
    stats = counter.get_stats()
    
    # Fond semi-transparent pour les statistiques
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (380, 170), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Texte principal - Nombre de jongles
    juggle_text = f"JONGLES: {counter.juggle_count}"
    cv2.putText(frame, juggle_text, (20, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    
    # Statistiques détaillées
    cv2.putText(frame, f"Touches: {counter.total_touches}", (20, 80),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    cv2.putText(frame, f"Duree: {stats['duree_session']:.0f}s", (20, 100),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    cv2.putText(frame, f"Rythme: {stats['jongles_par_minute']:.1f}/min", (20, 120),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Affichage intervalle moyen si disponible
    if stats['rythme_moyen'] > 0:
        cv2.putText(frame, f"Intervalle moy: {stats['rythme_moyen']:.2f}s", (20, 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    
    # Indicateur de progression vers le prochain milestone
    next_milestone = ((counter.juggle_count // 10) + 1) * 10
    progress_to_milestone = counter.juggle_count % 10
    cv2.putText(frame, f"Prochain BIP: {next_milestone} ({progress_to_milestone}/10)", (20, 160),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    # État de détection
    if ball_pos:
        status = "BALLE DETECTEE"
        status_color = (0, 255, 0)
        # Dessiner la balle détectée
        cv2.circle(frame, ball_pos, ball_radius, (0, 255, 0), 2)
        cv2.circle(frame, ball_pos, 3, (0, 255, 0), -1)
        
        # Afficher le rayon
        cv2.putText(frame, f"r:{ball_radius}px", (ball_pos[0] + ball_radius + 5, ball_pos[1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    else:
        status = "RECHERCHE BALLE..."
        status_color = (0, 165, 255)
    
    cv2.putText(frame, status, (20, height - 60),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
    
    # Instructions avec mention du bip
    cv2.putText(frame, "SPACE: Reset | R: Stats | BIP tous les 10 | Q: Quitter", (20, height - 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

def main():
    """
    Fonction principale du compteur de jongles avec BIP
    """
    print("🟡 COMPTEUR DE JONGLES - SPIKEBALL 🟡")
    print("=" * 45)
    print("Fonctionnalités:")
    print("- 🔔 BIP SONORE tous les 10 jongles !")
    print("- 📊 Statistiques temps réel")
    print("- 🎯 Comptage précis des jongles")
    print("- 🌈 Trajectoire colorée")
    print("=" * 45)
    print("Instructions:")
    print("- Positionne ta balle jaune devant la caméra")
    print("- Commence à jongler !")
    print("- Écoute le BIP tous les 10 jongles ! 🔔")
    print("- ESPACE: Remettre les compteurs à zéro")
    print("- R: Afficher les statistiques détaillées")
    print("- Q: Quitter")
    print("=" * 45)
    
    # Test du son au démarrage
    print("🔊 Test du système audio...")
    try:
        winsound.Beep(1000, 200)  # Bip de test
        print("✅ Son fonctionnel - Tu entendras les bips !")
    except Exception as e:
        print(f"⚠️ Son indisponible: {e}")
        print("   Les bips seront remplacés par des messages console")
    
    # Initialiser la caméra
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erreur: Impossible d'ouvrir la caméra")
        return
    
    # Régler la résolution pour de meilleures performances
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Initialiser le compteur
    counter = JuggleCounter()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Erreur de lecture caméra")
                break
            
            # Détecter la balle
            ball_pos, ball_radius = detect_yellow_ball(frame)
            
            # Mettre à jour le compteur
            counter.update(ball_pos, ball_radius)
            
            # Dessiner la trajectoire
            draw_trajectory(frame, counter)
            
            # Dessiner l'interface
            draw_hud(frame, counter, ball_pos, ball_radius)
            
            # Afficher l'image
            cv2.imshow('🟡 Compteur de Jongles avec BIP', frame)
            
            # Gestion des touches
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' '):  # ESPACE pour reset
                counter = JuggleCounter()
                print("🔄 Compteurs remis à zéro - Prêt pour une nouvelle session !")
            elif key == ord('r'):  # R pour statistiques
                print_detailed_stats(counter)
    
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du programme")
    
    finally:
        # Afficher les statistiques finales
        print("\n" + "=" * 45)
        print("📊 STATISTIQUES FINALES")
        print_detailed_stats(counter)
        
        # Bip de fin
        try:
            winsound.Beep(800, 300)  # Bip de fin plus grave
            print("🔔 Session terminée !")
        except:
            print("📊 Session terminée !")
        
        # Libérer les ressources
        cap.release()
        cv2.destroyAllWindows()

def print_detailed_stats(counter):
    """
    Affiche les statistiques détaillées avec info sur les milestones
    """
    stats = counter.get_stats()
    
    print("=" * 45)
    print(f"🟡 JONGLES RÉUSSIS: {stats['jongles']}")
    print(f"✋ TOUCHES TOTALES: {stats['touches_totales']}")
    print(f"⏱️  DURÉE SESSION: {stats['duree_session']:.1f} secondes")
    print(f"📈 RYTHME: {stats['jongles_par_minute']:.1f} jongles/minute")
    
    if stats['rythme_moyen'] > 0:
        print(f"🎯 INTERVALLE MOYEN: {stats['rythme_moyen']:.2f} secondes")
    
    # Calcul des milestones atteints
    milestones_reached = counter.juggle_count // 10
    if milestones_reached > 0:
        print(f"🔔 BIPS ENTENDUS: {milestones_reached} (tous les 10 jongles)")
        print(f"🎉 MILESTONES ATTEINTS: {[i*10 for i in range(1, milestones_reached+1)]}")
    
    # Analyse des intervalles
    if counter.juggle_intervals:
        intervals = counter.juggle_intervals
        print(f"📊 ANALYSE DES INTERVALLES:")
        print(f"   🔸 Plus court: {min(intervals):.2f}s")
        print(f"   🔸 Plus long: {max(intervals):.2f}s")
        print(f"   🔸 Écart-type: {np.std(intervals):.2f}s")
        
        # Régularité
        if np.std(intervals) < 0.5:
            print("🎯 RÉGULARITÉ: Excellent ! Rythme très constant")
        elif np.std(intervals) < 1.0:
            print("👍 RÉGULARITÉ: Bon rythme, assez régulier")
        else:
            print("💪 RÉGULARITÉ: Rythme variable, continue à t'entraîner")
    
    # Évaluation de performance avec encouragements
    if stats['jongles'] >= 100:
        print("🏆🏆🏆 INCROYABLE ! Tu es un MAÎTRE du jonglage !")
        print(f"🎊 {milestones_reached} bips entendus - Performance légendaire !")
    elif stats['jongles'] >= 50:
        print("🏆 EXCELLENT ! Tu es un pro du jonglage !")
        print(f"🎉 {milestones_reached} milestones franchies !")
    elif stats['jongles'] >= 20:
        print("👍 TRÈS BIEN ! Continue comme ça !")
        if milestones_reached >= 2:
            print(f"🔔 {milestones_reached} bips - Tu progresses bien !")
    elif stats['jongles'] >= 10:
        print("👌 PAS MAL ! Tu progresses !")
        if milestones_reached >= 1:
            print("🎵 Premier bip atteint - Bravo !")
    else:
        next_milestone = 10
        remaining = next_milestone - stats['jongles']
        print("💪 CONTINUE ! L'entraînement paie toujours !")
        print(f"🎯 Plus que {remaining} jongles pour ton premier BIP !")
    
    # Conseils basés sur le rythme
    if stats['rythme_moyen'] > 0:
        if stats['rythme_moyen'] < 0.8:
            print("💡 CONSEIL: Rythme rapide ! Essaie de ralentir pour plus de contrôle")
        elif stats['rythme_moyen'] > 2.0:
            print("💡 CONSEIL: Tu peux accélérer un peu le rythme")
        else:
            print("💡 CONSEIL: Bon rythme de jonglage !")
    
    print("=" * 45)

if __name__ == "__main__":
    main()