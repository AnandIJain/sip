import time
import bs4

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from sips.lines.bov import better

ROOT_URL = 'https://www.bovada.lv/'
GAME_CLASS = 'coupon-content'
MARKETS_CLASS = 'markets-container'
BET_BUTTON_CLASS = 'bet-btn'
SELECTED_BETS_CLASS = 'bet-btn selected'

IGNORE_FLAG_ID = 'custom-checkbox'
ALERT_CLASS_NAME = 'sp-overlay-alert__button'

RISK_ID = 'default-input--risk'
WIN_AMT_ID = 'default-input--win'

RISK_AMT_DIV_NAME = 'custom-field risk-field'
WIN_AMT_DIV_NAME = 'custom-field win-field'

TOP_LINE_CLASS = 'top-line'


MARKET_NAMES = {
    0: 'point_spread',
    1: 'money_line',
    2: 'over_under'
}


def get_games(driver, verbose=False):
    '''
    uses selenium to find the 'coupon-content'(s)
    each game has a tag_name of 'section'
    '''

    games = driver.find_elements_by_class_name(GAME_CLASS)

    if verbose:
        print(f'len(games): {len(games)}')
        _ = [print(g.text) for g in games]

    return games


def mkts_from_game(game, verbose=False):

    game_mkts = game.find_elements_by_class_name(MARKETS_CLASS)

    if verbose:
        _ = [print(mkt.text) for mkt in game_mkts]

    return game_mkts


def get_mkts(games, verbose=False):
    '''
    returns MARKETS_CLASS class name with selenium
    '''
    mkts = []

    for game in games:
        game_mkts = mkts_from_game(game, verbose=verbose)
        mkts += game_mkts

    if verbose:
        print(f'len(mkts): {len(mkts)}')
    return mkts


def buttons_from_mkts(mkts, verbose=False):
    '''
    returns list of buttons for each market provided
    '''
    buttons = []
    for mkt in mkts:
        mkt_buttons = mkt.find_elements_by_class_name(BET_BUTTON_CLASS)
        buttons += mkt_buttons
    if verbose:
        print(f'len(buttons): {len(buttons)}')
        _ = [print(button.text) for button in buttons]
    return buttons
    

def get_bet_buttons(element):
    '''
    for a selenium object, find all of the classes w/ name 'bet-btn'
    '''
    bet_buttons = element.find_elements_by_class_name(BET_BUTTON_CLASS)
    return bet_buttons


def bet_buttons_via_games(driver=None, verbose=False):
    '''
    possibly equivalent to driver.find_elements_by_class_name('bet-btn')
    see get_bet_buttons in bet_utils.py
    '''
    if not driver:
        driver = better.get_driver()

    games = get_games(driver, verbose=verbose)
    mkts = get_mkts(games, verbose=verbose)
    buttons = buttons_from_mkts(mkts, verbose=verbose)
    return buttons


def locate_btn(game, team_name, mkt_type, verbose=False):
    '''
    given selenium game, team_name, and mkt_type
    returns find the specific bet button for the givens 

    game: selenium obj
    team_name: str
    mkt_type: 0 is point spread, 1 is moneyline, and 2 is over/under
    '''
    bet_buttons = get_bet_buttons(game)
    index = btn_index(game, mkt_type, team_name)
    to_click = bet_buttons[index]

    if verbose:
        print(f'btn_index: {index}')

    return to_click


def to_soup(driver):
    '''
    driver is selenium webdriver
    '''
    p = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    return p


def find_bet_button(team_name, mkt_type, driver, verbose=False):
    gs = get_games(driver)
    g = game_from_team_name(gs, team_name, verbose=verbose)
    if not g:
        print(f'wtf')

    buttons = get_bet_buttons(g)
    index = btn_index(g, mkt_type, team_name)
    to_click = buttons[index]
    driver.execute_script("return arguments[0].scrollIntoView();", to_click)

    if verbose:
        print(f'game: {g}')
        print(f'len buttons: {len(buttons)}')
        for i, button in enumerate(buttons):
            print(f'button{[i]}: {button.text}')

    return to_click


def game_from_team_name(games, team_name, verbose=False):
    '''
    rn just takes in 1 game => double header issue for mlb
    '''
    for game in games:
        teams = teams_from_game(game)
        if team_name in teams:
            if verbose:
                print(f'found {team_name} game')
            return game
    if verbose:
        print(f'{team_name} game NOT found')
    return None


def team_names_from_games(games, zip_out=False, verbose=False):
    dogs = []
    favs = []
    for game in games:
        dog, fav = teams_from_game(game, verbose=verbose)
        dogs.append(dog)
        favs.append(fav)
    if zip_out:
        ret = list(zip(dogs, favs))
    else:
        ret = (dogs, favs)
    return ret


def btn_index(game, mkt_type, team_name='Washington Redskins'):

    teams = teams_from_game(game)

    if team_name == teams[0]:
        is_fav = False
    else:
        is_fav = True

    index = mkt_type * 2 + int(is_fav)
    return index


def teams_from_game(game, verbose=False):
    names = game.find_elements_by_tag_name('h4')
    dog = names[0].text
    fav = names[1].text

    if verbose:
        print(f'dog: {dog}')
        print(f'fav: {fav}\n')
    return dog, fav


def set_wager(driver, index, amt):
    '''
    assumes that there is something in the betslip
    '''
    
    wager_boxes = driver.find_elements_by_id(RISK_ID)

    try:
        wager_box = wager_boxes[index]
    except IndexError:
        accept_review_step_skip(driver)

        wager_boxes = driver.find_elements_by_id(RISK_ID)
        wager_box = wager_boxes[index]
        
    wager_box.send_keys(amt)


def trigger_review_slip_alert(driver, buttons=None):
    '''
    program clicks a button to trigger the betslip alert,
    which it then accepts
    '''

    if not buttons:
        buttons = bet_buttons_via_games(driver)
    print(f'buttons: {buttons}')
    button = buttons[0]
    button.send_keys('\n')
    # button.click()
    time.sleep(1)
    accept_review_step_skip(driver)


def accept_review_step_skip(driver):
    '''
    accepts the review slip alert
    '''
    labels = driver.find_elements_by_tag_name('label')
    label = labels[7]
    label.click()
    button = driver.find_element_by_class_name(ALERT_CLASS_NAME)
    button.send_keys('\n')
    time.sleep(1.5)


def get_team_names(driver):
    '''
    gets the team names of all teams on current driver page
    '''
    name_elements = driver.find_elements_by_class_name('name')
    team_names = [name.text for name in name_elements]
    return team_names


def base_driver(screen=None):
    '''
    screen is either None, 'full', or 'min'
    '''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")

    driver = webdriver.Chrome(chrome_options=chrome_options)

    if not screen:
        pass
    elif screen == 'full':
        driver.maximize_window()
    elif screen == 'min':
        driver.minimize_window()

    return driver

