.PHONY: install test test-smoke test-web test-mobile test-all lint format report clean

# 安装依赖
install:
	pip install -r requirements.txt
	playwright install chromium --with-deps

# 运行所有测试
test:
	pytest tests/ -v --tb=short

# 运行冒烟测试
test-smoke:
	pytest tests/ -m smoke -v --tb=short

# 运行Web端测试
test-web:
	pytest tests/web/ -m web -v --tb=short

# 运行移动端测试
test-mobile:
	pytest tests/mobile/ -m mobile -v --tb=short

# 运行所有浏览器和移动端测试
test-all:
	pytest tests/ -v --tb=short -m "web or mobile"

# 并行执行测试
test-parallel:
	pytest tests/ -n auto -v --tb=short

# 代码检查
lint:
	ruff check . --ignore E501 || true

# 代码格式化
format:
	ruff format . || true
	black . || true

# 生成报告
report:
	pytest tests/ --html=reports/report.html --self-contained-html

# 清理临时文件
clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache
	rm -rf tests/__pycache__ tests/web/__pycache__ tests/mobile/__pycache__
	rm -rf pages/__pycache__ pages/base/__pycache__ pages/web/__pycache__
	rm -rf components/__pycache__ utils/__pycache__ configs/__pycache__
	rm -f auth.json
	rm -rf reports/*.html reports/*.xml
	rm -rf screenshots/*.png screenshots/*.html
	rm -rf traces/*.zip

# 安装浏览器
install-browsers:
	playwright install chromium
	playwright install firefox
	playwright install webkit

# 更新依赖
freeze:
	pip freeze > requirements.txt
