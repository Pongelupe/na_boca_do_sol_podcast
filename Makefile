.PHONY: build dev generate add index update deploy docker clean podcast podcast-local batch mp3 upload instagram rss

# Frontend
build: generate rss
	cd frontend && npm install && npm run build

dev: generate
	cd frontend && npm run dev

generate: clean-content
	cd frontend && python3 generate_content.py

# Content management
add:
	./tools/add_episode.sh $(FOLDER)

index:
	mkdir -p $(DIR)
	python3 tools/index_to_md.py $(URL) $(DIR) > $(DIR)/README.md

# Cleanup
clean:
	rm -rf frontend/node_modules frontend/dist frontend/.astro frontend/src/content/authors frontend/src/content/books

clean-content:
	rm -rf frontend/src/content/authors/*.md
	rm -rf frontend/src/content/books/*.md
	rm -rf frontend/src/content/episodes/*.md

# Podcast generation
podcast:
	cd podcast && docker run -v ./:/app --gpus all nbsp $(URL)

podcast-local:
	cd podcast && pip install -q -r requirements.txt && ./podcast.sh $(URL)

batch:
	cd podcast && ./batch_podcast.sh $(FILE)

docker:
	cd podcast && docker build -t nbsp .

# S3
mp3:
	find arquivos -name "*.wav" -exec sh -c 'mp3="$${1%.wav}.mp3"; [ -f "$$mp3" ] || sudo ffmpeg -i "$$1" -q:a 2 "$$mp3"' _ {} \;

zip: mp3
	@find arquivos -name "book.json" -exec sh -c ' \
		book_dir=$$(dirname "$$1"); \
		book_name=$$(basename "$$book_dir"); \
		author_dir=$$(dirname "$$book_dir"); \
		author=$$(basename "$$author_dir"); \
		zip_path="$$author_dir/$$book_name.zip"; \
		mp3s=$$(find "$$book_dir" -name "*.mp3" | sort); \
		if [ -n "$$mp3s" ]; then \
			rm -f "$$zip_path"; \
			echo "$$mp3s" | xargs zip -j "$$zip_path"; \
			echo "📦 $$author/$$book_name.zip"; \
		fi \
	' _ {} \;

upload: zip
	aws s3 sync arquivos/ s3://nbds-podcast/ --exclude "*.txt" --exclude "*.md" --exclude "*.json" --exclude "*.html" --exclude "*.wav"

deploy: upload
	@echo "✅ Audio synced. Push to main to deploy site."

# RSS
rss:
	python3 tools/generate_rss.py --output frontend/public/feed.xml

# Instagram
VENV := tools/.venv
$(VENV):
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -r tools/requirements.txt

instagram: $(VENV)
	$(VENV)/bin/python tools/generate_instagram.py --episode "$(EPISODE)" $(if $(THEME),--theme $(THEME))