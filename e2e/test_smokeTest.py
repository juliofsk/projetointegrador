from playwright.sync_api import Page, expect

def test_home_login(page: Page):
    page.goto("/")
    expect(page).to_have_title("Document")
    page.pause()
    page.click("text=Login")
    page.pause()
    expect(page).to_have_url("/login")
    page.fill("input[name='nome']", "julio")
    page.pause()
    page.fill("input[name='senha']", "123")
    page.pause()
    page.click("text=Entrar") 
    page.pause()