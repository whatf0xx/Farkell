from game import InputType, Player


def test_lazy_bank(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "1 1 1 2 3 4")
    bot = Player("Bot", InputType.USER, InputType.COM, "LAZY-BANK")
    return_value = bot.turn()
    assert bot.score == 300
    assert return_value == 300
