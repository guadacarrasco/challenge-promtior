#!/bin/bash
# Development utility script

set -e

show_menu() {
    echo ""
    echo "Promtior RAG - Development Menu"
    echo "================================"
    echo "1. Start services (docker-compose up)"
    echo "2. Stop services (docker-compose down)"
    echo "3. View logs (follow all services)"
    echo "4. View logs (backend only)"
    echo "5. Restart backend"
    echo "6. Re-initialize vector store"
    echo "7. Run backend tests"
    echo "8. Check API health"
    echo "9. Clean Docker resources"
    echo "10. Interactive shell"
    echo "0. Exit"
    echo ""
    read -p "Select option (0-10): " choice
}

case "$1" in
    start)
        echo "Starting services..."
        docker-compose up -d
        echo "✅ Services started"
        ;;
    stop)
        echo "Stopping services..."
        docker-compose down
        echo "✅ Services stopped"
        ;;
    logs)
        docker-compose logs -f
        ;;
    logs-backend)
        docker-compose logs -f backend
        ;;
    restart-backend)
        echo "Restarting backend..."
        docker-compose restart backend
        echo "✅ Backend restarted"
        ;;
    init-vector-store)
        echo "Initializing vector store..."
        curl -X POST http://localhost:8000/api/init
        echo ""
        echo "✅ Vector store initialized"
        ;;
    test)
        echo "Running backend tests..."
        cd backend
        pip install -e ".[dev]"
        pytest tests/ -v
        ;;
    health)
        echo "Checking API health..."
        curl -s http://localhost:8000/api/health | jq . || echo "API not responding"
        ;;
    clean)
        echo "Cleaning Docker resources..."
        docker-compose down
        docker system prune -f
        echo "✅ Cleaned"
        ;;
    shell)
        docker-compose exec backend /bin/bash
        ;;
    -h|--help)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start               - Start services"
        echo "  stop                - Stop services"
        echo "  logs                - View all logs"
        echo "  logs-backend        - View backend logs"
        echo "  restart-backend     - Restart backend service"
        echo "  init-vector-store   - Initialize vector store"
        echo "  test                - Run backend tests"
        echo "  health              - Check API health"
        echo "  clean               - Clean Docker resources"
        echo "  shell               - Enter backend container shell"
        echo "  (no args)           - Interactive menu"
        ;;
    *)
        show_menu
        
        case $choice in
            1) $0 start ;;
            2) $0 stop ;;
            3) $0 logs ;;
            4) $0 logs-backend ;;
            5) $0 restart-backend ;;
            6) $0 init-vector-store ;;
            7) $0 test ;;
            8) $0 health ;;
            9) $0 clean ;;
            10) $0 shell ;;
            0) echo "Goodbye!"; exit 0 ;;
            *) echo "Invalid option"; exit 1 ;;
        esac
        ;;
esac
