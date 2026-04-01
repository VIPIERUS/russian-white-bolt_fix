#!/bin/bash
# =============================================================================
# Скрипт инициализации VPN Auto-Updater репозитория
# Использование: ./init-repo.sh [GITVERSE_REPO_URL]
# =============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции вывода
print_header() {
    echo ""
    echo "============================================================================="
    echo "$1"
    echo "============================================================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    print_header "🔍 Проверка зависимостей"
    
    local deps=("git" "python3" "pip3")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v $dep &> /dev/null; then
            missing+=($dep)
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_error "Отсутствуют зависимости: ${missing[*]}"
        print_info "Установите их и попробуйте снова"
        exit 1
    fi
    
    print_success "Все зависимости установлены"
}

# Установка Python пакетов
install_python_deps() {
    print_header "📦 Установка Python зависимостей"
    
    if [ -f "requirements.txt" ]; then
        pip3 install -q -r requirements.txt
        print_success "Python пакеты установлены"
    else
        print_warning "requirements.txt не найден, пропускаем"
    fi
}

# Создание структуры папок
create_directories() {
    print_header "📁 Создание структуры папок"
    
    mkdir -p VPNMIRRORS
    mkdir -p scripts
    mkdir -p sources
    mkdir -p .github/workflows
    
    print_success "Папки созданы"
}

# Проверка файлов
verify_files() {
    print_header "📋 Проверка файлов"
    
    local files=(
        "scripts/fetch_configs.py"
        "scripts/generate_readme.py"
        "sources/urls.txt"
        ".github/workflows/update-vpn.yml"
        "requirements.txt"
    )
    
    local missing=()
    
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            missing+=($file)
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_error "Отсутствуют файлы: ${missing[*]}"
        print_info "Убедитесь что вы скопировали все файлы проекта"
        exit 1
    fi
    
    print_success "Все необходимые файлы на месте"
}

# Тестовый запуск скриптов
test_scripts() {
    print_header "🧪 Тестовый запуск скриптов"
    
    print_info "Запуск fetch_configs.py..."
    if python3 scripts/fetch_configs.py; then
        print_success "fetch_configs.py выполнен успешно"
    else
        print_error "fetch_configs.py завершился с ошибкой"
        print_info "Проверьте sources/urls.txt и интернет-соединение"
    fi
    
    if [ -f "VPNMIRRORS/metadata.json" ]; then
        print_info "Запуск generate_readme.py..."
        if python3 scripts/generate_readme.py; then
            print_success "generate_readme.py выполнен успешно"
        else
            print_error "generate_readme.py завершился с ошибкой"
        fi
    fi
}

# Показать статистику
show_stats() {
    print_header "📊 Статистика"
    
    if [ -f "VPNMIRRORS/metadata.json" ]; then
        echo "Файлов в VPNMIRRORS:"
        find VPNMIRRORS -type f ! -name "metadata.json" 2>/dev/null | wc -l | xargs echo "  - Конфигурационных файлов:"
        
        echo ""
        echo "Размер папки VPNMIRRORS:"
        du -sh VPNMIRRORS 2>/dev/null || echo "  N/A"
        
        echo ""
        echo "Конфигов по категориям:"
        for dir in VPNMIRRORS/*/; do
            if [ -d "$dir" ]; then
                local cat=$(basename "$dir")
                local count=$(find "$dir" -type f 2>/dev/null | wc -l)
                echo "  - $cat: $count файлов"
            fi
        done
    else
        print_warning "metadata.json не найден, статистика недоступна"
    fi
}

# Главная функция
main() {
    print_header "🚀 Инициализация VPN Auto-Updater"
    
    check_dependencies
    create_directories
    verify_files
    install_python_deps
    test_scripts
    show_stats
    
    print_header "✅ Инициализация завершена!"
    
    echo ""
    echo "📋 Следующие шаги:"
    echo ""
    echo "  1. Создайте репозиторий на GitVerse.ru"
    echo "  2. Добавьте секрет GITVERSE_TOKEN в настройках репозитория"
    echo "  3. Закоммитьте и запушьте файлы:"
    echo ""
    echo "     git add ."
    echo "     git commit -m 'Initial setup: VPN auto-updater'"
    echo "     git push origin master"
    echo ""
    echo "  4. Запустите workflow вручную в разделе Actions"
    echo ""
    echo "📖 Подробная инструкция в файле SETUP.md"
    echo ""
}

# Запуск
main "$@"
