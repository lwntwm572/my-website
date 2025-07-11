import pygame
import sys

# --- הגדרות ראשוניות ---
pygame.init()

# גודל המסך
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("משחק פלטפורמה בסיסי")

# צבעים (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0) # צבע לפלטפורמות

# הגדרות שחקן
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_COLOR = RED
player_x = 50
player_y = SCREEN_HEIGHT - PLAYER_HEIGHT - 50 # מתחיל קצת מעל התחתית
player_speed = 5
player_vel_y = 0  # מהירות אנכית (לקפיצה וכבידה)
is_jumping = False
on_ground = False

# הגדרות כבידה וקפיצה
GRAVITY = 1
JUMP_STRENGTH = -20 # כוח קפיצה (ערך שלילי כי Y גדל כלפי מטה)

# --- קלאס לשחקן (יותר מובנה, אבל נתחיל בפשטות כאן) ---
# כרגע נשתמש במשתנים גלובליים לשחקן לשם פשטות ההדגמה הראשונית.
# בהמשך נוכל להפוך את זה לקלאס מסודר.

player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)

# --- פלטפורמות ---
# רשימה של מלבני פלטפורמות (x, y, width, height)
platforms_data = [
    (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # רצפה ראשית
    (200, SCREEN_HEIGHT - 150, 150, 20),
    (400, SCREEN_HEIGHT - 250, 200, 20),
    (50, SCREEN_HEIGHT - 350, 100, 20),
    (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 450, 180, 20)
]
platforms = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in platforms_data]


# שעון משחק (לשליטה על קצב הפריימים)
clock = pygame.time.Clock()
FPS = 60

# --- לולאת המשחק הראשית ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # זמן שעבר מאז הפריים האחרון בשניות (לא בשימוש כרגע, אך טוב להמשך)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground: # קפיצה רק אם על הקרקע
                is_jumping = True
                player_vel_y = JUMP_STRENGTH
                on_ground = False

    # --- קלט מהמקלדת לתנועה אופקית ---
    keys = pygame.key.get_pressed()
    new_player_x = player_rect.x

    if keys[pygame.K_LEFT]:
        new_player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        new_player_x += player_speed
    
    # יצירת מלבן זמני למיקום החדש לבדיקת התנגשות אופקית
    potential_player_rect_x = pygame.Rect(new_player_x, player_rect.y, PLAYER_WIDTH, PLAYER_HEIGHT)
    
    # בדיקת התנגשות אופקית עם פלטפורמות
    x_collision = False
    for plat in platforms:
        if potential_player_rect_x.colliderect(plat):
            x_collision = True
            # טיפול בהיתקעות בצדדים (מניעת חדירה)
            if keys[pygame.K_RIGHT] and new_player_x < plat.left : # זז ימינה ונתקע בצד שמאל של הפלטפורמה
                 potential_player_rect_x.right = plat.left
            elif keys[pygame.K_LEFT] and new_player_x + PLAYER_WIDTH > plat.right: # זז שמאלה ונתקע בצד ימין של הפלטפורמה
                 potential_player_rect_x.left = plat.right
            break # מספיקה התנגשות אחת
    
    if not x_collision:
        player_rect.x = potential_player_rect_x.x
    else:
        player_rect.x = potential_player_rect_x.x # עדכון למיקום המתוקן אחרי התנגשות צד

    # הגבלת תנועה אופקית לגבולות המסך
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > SCREEN_WIDTH:
        player_rect.right = SCREEN_WIDTH

    # --- לוגיקת המשחק (עדכונים) ---
    # כבידה
    player_vel_y += GRAVITY
    if player_vel_y > 15: # מהירות נפילה מקסימלית (למניעת נפילה מהירה מדי)
        player_vel_y = 15
    
    new_player_y = player_rect.y + player_vel_y

    # יצירת מלבן זמני למיקום החדש לבדיקת התנגשות אנכית
    potential_player_rect_y = pygame.Rect(player_rect.x, new_player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
    on_ground_this_frame = False # לבדוק אם נחתנו בפריים הנוכחי

    # בדיקת התנגשות אנכית עם פלטפורמות
    for plat in platforms:
        if potential_player_rect_y.colliderect(plat):
            if player_vel_y > 0: # נופל למטה
                potential_player_rect_y.bottom = plat.top # נחיתה על הפלטפורמה
                player_vel_y = 0 # עצירת הנפילה
                is_jumping = False # סימון שהקפיצה הסתיימה
                on_ground_this_frame = True # השחקן על הקרקע
            elif player_vel_y < 0: # קופץ למעלה ונתקל בתחתית פלטפורמה
                potential_player_rect_y.top = plat.bottom
                player_vel_y = 0 # עצירת העלייה
            break # מספיקה התנגשות אחת

    player_rect.y = potential_player_rect_y.y
    on_ground = on_ground_this_frame

    # הגבלת תנועה אנכית לתחתית המסך (למקרה שאין פלטפורמת רצפה מלאה)
    # או למקרה שנופלים מהצדדים
    if player_rect.bottom > SCREEN_HEIGHT:
        player_rect.bottom = SCREEN_HEIGHT
        player_vel_y = 0
        is_jumping = False
        on_ground = True


    # --- ציור (Rendering) ---
    screen.fill(WHITE)  # צבע רקע לבן

    # ציור השחקן
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

    # ציור הפלטפורמות
    for plat in platforms:
        pygame.draw.rect(screen, GREEN, plat)

    pygame.display.flip()  # עדכון כל המסך

# --- סיום ---
pygame.quit()
sys.exit()