from game import InputType, Player


def test_lazy_bank_score(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "1 1 1 2 3 4")
    bot = Player("Bot", InputType.USER, InputType.COM, "LAZY-BANK")
    return_value = bot.turn()
    assert bot.score == 300
    assert return_value == 300


def test_laz_bank_naming(monkeypatch, capfd):
    monkeypatch.setattr('builtins.input', lambda _: "1 1 1 2 3 4")
    bot = Player("Bot", InputType.USER, InputType.COM, "LAZY-BANK")
    bot.turn()

    def capture_output():
        yield capfd.readouterr().out

    captured = capture_output()
    assert next(captured) == "THREE OF A KIND\n"
